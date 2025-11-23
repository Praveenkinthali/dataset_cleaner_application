# presentation_layer/VisualizeWindow.py

import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VisualizeWindow(tk.Frame):
    def __init__(self, master):
        self.light_bg = getattr(master, 'light_bg', '#f8f9fa')
        self.primary_color = getattr(master, 'primary_color', '#2c3e50')
        self.accent_color = getattr(master, 'accent_color', '#3498db')
        self.success_color = getattr(master, 'success_color', '#27ae60')
        self.danger_color = getattr(master, 'danger_color', '#e74c3c')
        
        super().__init__(master, bg=self.light_bg)
        self.master = master

        # UPDATED: Use dataset_manager to get dataframe
        self.df = self.get_dataframe()
        self.status_var = tk.StringVar(value="Ready to visualize data")
        plt.style.use('seaborn-v0_8')

        main_container = tk.Frame(self, bg=self.light_bg)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.light_bg)
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Button(header_frame, text="← Back to Main", bg="#95a5a6", fg="white",
                 command=lambda: master.show_frame(master.MainMenu),
                 font=("Arial", 10), padx=15).pack(side="left", padx=(0, 20))
        
        title_frame = tk.Frame(header_frame, bg=self.light_bg)
        title_frame.pack(side="left", expand=True)
        
        tk.Label(title_frame, text="Data Visualization Studio", font=("Arial", 24, "bold"),
                fg=self.primary_color, bg=self.light_bg).pack()
        tk.Label(title_frame, text="Create custom charts and visualizations",
                font=("Arial", 11), fg="#7f8c8d", bg=self.light_bg).pack()

        # Controls
        controls_frame = tk.LabelFrame(main_container, text="Chart Controls",
                                      font=("Arial", 11, "bold"), fg=self.primary_color,
                                      bg=self.light_bg)
        controls_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        col_sel_frame = tk.Frame(controls_frame, bg=self.light_bg)
        col_sel_frame.pack(fill="x", padx=10, pady=15)
        
        # X Axis
        x_frame = tk.Frame(col_sel_frame, bg=self.light_bg)
        x_frame.pack(side="left", padx=(0, 20))
        tk.Label(x_frame, text="X Axis:", font=("Arial", 10, "bold"), bg=self.light_bg).pack(side="left", padx=(0, 10))
        self.x_var = tk.StringVar()
        self.x_menu = ttk.Combobox(x_frame, textvariable=self.x_var, state="readonly", width=20)
        self.x_menu.pack(side="left")
        
        # Y Axis
        y_frame = tk.Frame(col_sel_frame, bg=self.light_bg)
        y_frame.pack(side="left", padx=(0, 20))
        tk.Label(y_frame, text="Y Axis:", font=("Arial", 10, "bold"), bg=self.light_bg).pack(side="left", padx=(0, 10))
        self.y_var = tk.StringVar()
        self.y_menu = ttk.Combobox(y_frame, textvariable=self.y_var, state="readonly", width=20)
        self.y_menu.pack(side="left")
        
        # Plot Type
        plot_frame = tk.Frame(col_sel_frame, bg=self.light_bg)
        plot_frame.pack(side="left", padx=(0, 20))
        tk.Label(plot_frame, text="Plot Type:", font=("Arial", 10, "bold"), bg=self.light_bg).pack(side="left", padx=(0, 10))
        self.plot_var = tk.StringVar(value="auto")
        self.plot_type_menu = ttk.Combobox(plot_frame, textvariable=self.plot_var, state="readonly",
                                          values=["auto", "histogram", "scatter", "boxplot", "bar", "pie", "line"],
                                          width=14)
        self.plot_type_menu.pack(side="left")
        
        # Plot Button
        tk.Button(col_sel_frame, text="📊 Generate Plot", command=self.plot_chart,
                 bg=self.success_color, fg="white", font=("Arial", 10, "bold"),
                 padx=20).pack(side="left")

        # Chart container
        chart_container = tk.LabelFrame(main_container, text="Chart Preview",
                                       font=("Arial", 11, "bold"), fg=self.primary_color,
                                       bg=self.light_bg)
        chart_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chart_frame = tk.Frame(chart_container, bg=self.light_bg)
        self.chart_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.canvas = None

        # Status bar
        tk.Label(main_container, textvariable=self.status_var, relief="sunken",
                anchor="w", bg="#ecf0f1", font=("Arial", 9)).pack(fill="x", side="bottom", pady=(5, 0))
        
        self.refresh_columns()

    def get_dataframe(self):
        """Safely get dataframe from dataset_manager"""
        try:
            df = self.master.dataset_manager.get_dataframe()
            if df is None:
                return pd.DataFrame()
            return df
        except Exception as e:
            print(f"Error accessing dataframe: {e}")
            return pd.DataFrame()

    def refresh_columns(self):
        self.df = self.get_dataframe()
        choices = list(self.df.columns) if not self.df.empty else []
        self.x_menu["values"] = choices
        self.y_menu["values"] = ["(None)"] + choices
        if choices:
            self.x_var.set(choices[0])
            self.y_var.set("(None)")
            self.status_var.set(f"Dataset loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
        else:
            self.status_var.set("No dataset loaded")

    def plot_chart(self):
        self.df = self.get_dataframe()
        if self.df.empty:
            self.show_status("No dataset loaded", error=True)
            return
        
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        x = self.x_var.get()
        y = self.y_var.get()
        y_col = None if y == "(None)" else y
        chart_type = self.plot_var.get()
        
        try:
            s_x = self.df[x] if x in self.df else None
            s_y = self.df[y_col] if y_col and y_col in self.df else None
            
            plt.close("all")
            fig, ax = plt.subplots(figsize=(8, 5))
            
            if chart_type == "auto":
                chart_type = self.auto_plot_type(s_x, s_y)
            
            if chart_type == "histogram":
                if s_x is not None and pd.api.types.is_numeric_dtype(s_x):
                    ax.hist(s_x.dropna(), bins=30, alpha=0.7, color=self.accent_color, edgecolor="black")
                    ax.set_title(f'Histogram of {x}', fontsize=14, fontweight='bold')
                    ax.set_xlabel(x, fontweight='bold')
                    ax.set_ylabel("Frequency", fontweight='bold')
                    ax.grid(True, alpha=0.3)
                else:
                    self.show_message_plot(ax, "Choose a numeric X axis for histogram.")
            
            elif chart_type == "scatter":
                if s_y is not None and pd.api.types.is_numeric_dtype(s_x) and pd.api.types.is_numeric_dtype(s_y):
                    ax.scatter(s_x, s_y, color=self.accent_color, alpha=0.7)
                    ax.set_title(f'Scatter Plot: {x} vs {y_col}', fontsize=14, fontweight='bold')
                    ax.set_xlabel(x, fontweight='bold')
                    ax.set_ylabel(y_col, fontweight='bold')
                    ax.grid(True, alpha=0.3)
                else:
                    self.show_message_plot(ax, "Need X & Y as numeric columns for scatter plot.")
            
            elif chart_type == "boxplot":
                if s_y is not None and pd.api.types.is_numeric_dtype(s_y):
                    self.df.boxplot(column=y_col, by=x, ax=ax)
                    ax.set_title(f'Box Plot: {y_col} by {x}', fontsize=14, fontweight='bold')
                elif pd.api.types.is_numeric_dtype(s_x):
                    ax.boxplot(s_x.dropna())
                    ax.set_title(f'Box Plot: {x}', fontsize=14, fontweight='bold')
                else:
                    self.show_message_plot(ax, "Select a numeric column for box plot.")
            
            elif chart_type == "bar":
                if pd.api.types.is_categorical_dtype(s_x) or pd.api.types.is_object_dtype(s_x) or s_x.nunique() <= 20:
                    value_counts = s_x.value_counts().head(15)
                    bars = ax.bar(value_counts.index.astype(str), value_counts.values,
                                color=self.success_color, alpha=0.8)
                    ax.set_title(f'Bar Chart of {x}', fontsize=14, fontweight='bold')
                    ax.set_ylabel("Count", fontweight='bold')
                    ax.set_xticklabels(value_counts.index.astype(str), rotation=45, ha="right")
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
                else:
                    self.show_message_plot(ax, "Bar charts work best with categorical X (≤20 unique values).")
            
            elif chart_type == "pie":
                value_counts = s_x.value_counts().head(8)
                if not value_counts.empty:
                    colors = plt.cm.Set3(np.linspace(0, 1, len(value_counts)))
                    wedges, texts, autotexts = ax.pie(value_counts.values,
                                                      labels=value_counts.index.astype(str),
                                                      autopct="%1.1f%%", startangle=90,
                                                      colors=colors, textprops={'fontsize': 9})
                    ax.set_title(f'Pie Chart of {x}', fontsize=14, fontweight='bold')
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                else:
                    self.show_message_plot(ax, "Pie chart needs categorical X with data.")
            
            elif chart_type == "line":
                if s_y is not None and pd.api.types.is_numeric_dtype(s_x) and pd.api.types.is_numeric_dtype(s_y):
                    ax.plot(s_x, s_y, '-o', color=self.primary_color, linewidth=2, markersize=4)
                    ax.set_title(f'Line Plot: {y_col} over {x}', fontsize=14, fontweight='bold')
                    ax.set_xlabel(x, fontweight='bold')
                    ax.set_ylabel(y_col, fontweight='bold')
                    ax.grid(True, alpha=0.3)
                else:
                    self.show_message_plot(ax, "Need numeric X and Y for line plot.")
            else:
                self.show_message_plot(ax, f"Unknown plot type: {chart_type}")
            
            plt.tight_layout()
            
            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            self.show_status(f"✅ {chart_type.capitalize()} plot generated successfully")
        except Exception as e:
            self.show_status(f"❌ Plot Error: {str(e)}", error=True)

    def auto_plot_type(self, s_x, s_y):
        if s_y is not None and pd.api.types.is_numeric_dtype(s_x) and pd.api.types.is_numeric_dtype(s_y):
            return "scatter"
        elif pd.api.types.is_numeric_dtype(s_x):
            return "histogram"
        elif pd.api.types.is_object_dtype(s_x) or s_x.nunique() <= 8:
            return "pie"
        elif s_x.nunique() <= 20:
            return "bar"
        else:
            return "histogram"

    def show_message_plot(self, ax, message):
        ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12,
                color=self.danger_color, transform=ax.transAxes, fontweight='bold')
        ax.axis('off')
        self.show_status(f"⚠️ {message}", error=True)

    def show_status(self, message, error=False):
        self.status_var.set(message)
# presentation_layer/StatsWindow.py

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class StatsWindow(tk.Frame):
    def __init__(self, master):
        # Initialize colors
        self.light_bg = getattr(master, 'light_bg', '#f8f9fa')
        self.primary_color = getattr(master, 'primary_color', '#2c3e50')
        self.secondary_color = getattr(master, 'secondary_color', '#34495e')
        self.accent_color = getattr(master, 'accent_color', '#3498db')
        self.success_color = getattr(master, 'success_color', '#27ae60')
        self.danger_color = getattr(master, 'danger_color', '#e74c3c')
        self.light_text = getattr(master, 'light_text', '#7f8c8d')
        self.dark_text = getattr(master, 'dark_text', '#2c3e50')
        
        super().__init__(master, bg=self.light_bg)
        self.master = master
        
        # UPDATED: Use dataset_manager to get dataframe
        self.df = self.get_dataframe()
        
        # Initialize status_var early
        self.status_var = tk.StringVar(value="Initializing...")
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8')
        
        # Main container
        main_container = tk.Frame(self, bg=self.light_bg)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with back button
        header_frame = tk.Frame(main_container, bg=self.light_bg)
        header_frame.pack(fill="x", pady=(0, 20))
        
        back_btn = tk.Button(
            header_frame, 
            text="← Back to Main", 
            bg="#95a5a6", 
            fg="white",
            command=lambda: master.show_frame(master.MainMenu),
            font=("Arial", 10),
            padx=15
        )
        back_btn.pack(side="left", padx=(0, 20))

        title_frame = tk.Frame(header_frame, bg=self.light_bg)
        title_frame.pack(side="left", expand=True)
        
        tk.Label(
            title_frame, 
            text="Statistical Analysis", 
            font=("Arial", 24, "bold"), 
            fg=self.primary_color,
            bg=self.light_bg
        ).pack()
        
        tk.Label(
            title_frame, 
            text="Comprehensive dataset statistics and visualizations",
            font=("Arial", 11), 
            fg=self.light_text,
            bg=self.light_bg
        ).pack()

        # Control panel
        control_frame = tk.LabelFrame(
            main_container,
            text="Analysis Controls",
            font=("Arial", 11, "bold"),
            fg=self.primary_color,
            bg=self.light_bg,
            relief="groove",
            bd=1
        )
        control_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        # Column selection
        col_sel_frame = tk.Frame(control_frame, bg=self.light_bg)
        col_sel_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            col_sel_frame, 
            text="Select Column:", 
            font=("Arial", 10, "bold"),
            bg=self.light_bg,
            fg=self.dark_text
        ).pack(side="left", padx=(0, 10))
        
        self.col_var = tk.StringVar()
        self.col_dropdown = ttk.Combobox(
            col_sel_frame, 
            textvariable=self.col_var, 
            state="readonly", 
            width=40,
            font=("Arial", 9)
        )
        self.col_dropdown.pack(side="left", padx=5)
        
        tk.Label(
            col_sel_frame, 
            text="Chart Type:", 
            font=("Arial", 10, "bold"),
            bg=self.light_bg,
            fg=self.dark_text
        ).pack(side="left", padx=(20, 10))
        
        self.chart_var = tk.StringVar(value="auto")
        chart_combo = ttk.Combobox(
            col_sel_frame, 
            textvariable=self.chart_var, 
            values=["auto", "histogram", "boxplot", "density", "bar"],
            state="readonly", 
            width=12,
            font=("Arial", 9)
        )
        chart_combo.pack(side="left", padx=5)
        
        refresh_btn = tk.Button(
            col_sel_frame, 
            text="🔄 Refresh", 
            command=self.refresh_all,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 9, "bold"),
            width=10
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Bind events
        self.col_dropdown.bind("<<ComboboxSelected>>", self.on_column_change)
        chart_combo.bind("<<ComboboxSelected>>", self.on_chart_type_change)
        
        # Create tabs
        self.create_tabs(main_container)
        
        # Status bar
        status_bar = tk.Label(
            main_container, 
            textvariable=self.status_var, 
            relief="sunken", 
            anchor="w", 
            bg="#ecf0f1",
            font=("Arial", 9),
            fg=self.dark_text
        )
        status_bar.pack(fill="x", side="bottom", pady=(5, 0))
        
        # Initialize data
        self.initialize_data()

    def get_dataframe(self):
        """Safely extract DataFrame from DatasetManager"""
        try:
            df = self.master.dataset_manager.get_dataframe()
            if df is None:
                return pd.DataFrame()
            return df
        except Exception as e:
            print(f"Error accessing dataset: {e}")
            return pd.DataFrame()

    def on_column_change(self, event=None):
        """Handle column selection change"""
        self.refresh_details()
        self.refresh_plot()

    def on_chart_type_change(self, event=None):
        """Handle chart type change"""
        self.refresh_plot()

    def refresh_all(self):
        """Refresh all components"""
        self.df = self.get_dataframe()
        self.initialize_data()
        self.status_var.set("All components refreshed")

    def initialize_data(self):
        """Initialize dataset and UI components"""
        self.df = self.get_dataframe()
        
        if self.df is None or self.df.empty:
            if hasattr(self, 'col_dropdown'):
                self.col_dropdown["values"] = []
            self.status_var.set("No dataset loaded")
            return
        
        # Update dropdown with column names
        columns = list(self.df.columns)
        self.col_dropdown["values"] = columns
        if len(columns) > 0:
            self.col_var.set(columns[0])
        
        self.status_var.set(f"Loaded dataset: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
        
        # Populate all tabs
        self.populate_overview_tab()
        self.refresh_details()
        self.refresh_plot()

    def create_tabs(self, parent):
        """Create the tabbed interface"""
        self.tabs = ttk.Notebook(parent)
        self.tabs.pack(fill="both", expand=True)
        
        # Tab 1: Dataset Overview
        self.tab_overview = tk.Frame(self.tabs, bg=self.light_bg)
        self.tabs.add(self.tab_overview, text="📊 Overview")
        self.create_overview_tab()
        
        # Tab 2: Column Details
        self.tab_details = tk.Frame(self.tabs, bg=self.light_bg)
        self.tabs.add(self.tab_details, text="🔍 Details")
        self.create_details_tab()
        
        # Tab 3: Visualizations
        self.tab_vis = tk.Frame(self.tabs, bg=self.light_bg)
        self.tabs.add(self.tab_vis, text="📊 Charts")
        self.create_visualization_tab()

    def create_overview_tab(self):
        """Create dataset overview tab"""
        # Summary cards frame
        cards_frame = tk.Frame(self.tab_overview, bg=self.light_bg)
        cards_frame.pack(fill="x", padx=10, pady=10)
        self.cards_frame = cards_frame
        
        # Quick statistics table
        stats_frame = tk.LabelFrame(
            self.tab_overview,
            text="Column Overview",
            font=("Arial", 11, "bold"),
            fg=self.primary_color,
            bg=self.light_bg
        )
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree_frame = tk.Frame(stats_frame, bg=self.light_bg)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.overview_tree = ttk.Treeview(
            tree_frame,
            columns=("Column", "Type", "Missing", "Missing%", "Unique"),
            show="headings",
            height=12
        )
        
        columns_config = [
            ("Column", 150), ("Type", 100), ("Missing", 80), 
            ("Missing%", 80), ("Unique", 80)
        ]
        
        for col, width in columns_config:
            self.overview_tree.heading(col, text=col)
            self.overview_tree.column(col, width=width, anchor="center")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.overview_tree.yview)
        self.overview_tree.configure(yscrollcommand=scrollbar.set)
        
        self.overview_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def populate_overview_tab(self):
        """Populate the overview tab with data"""
        if self.df.empty:
            return
            
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        # Create summary cards
        cards_data = [
            ("Rows", f"{len(self.df):,}", self.accent_color),
            ("Columns", f"{len(self.df.columns):,}", self.primary_color),
            ("Missing Values", f"{self.df.isnull().sum().sum():,}", self.danger_color),
            ("Memory Usage", f"{self.df.memory_usage(deep=True).sum() / 1024**2:.1f} MB", self.success_color)
        ]
        
        for i, (title, value, color) in enumerate(cards_data):
            card = self.create_summary_card(self.cards_frame, title, value, color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.cards_frame.columnconfigure(i, weight=1)
        
        # Populate overview tree
        self.populate_overview_tree()

    def create_summary_card(self, parent, title, value, color):
        """Create a summary card widget"""
        card = tk.Frame(parent, relief="raised", borderwidth=1, bg="white")
        
        tk.Label(card, text=title, font=("Arial", 9, "bold"), 
                bg="white", fg=self.light_text).pack(pady=(8, 2))
        tk.Label(card, text=value, font=("Arial", 14, "bold"), 
                bg="white", fg=color).pack(pady=(2, 8))
        
        return card

    def create_details_tab(self):
        """Create tab for detailed column statistics"""
        details_container = tk.Frame(self.tab_details, bg=self.light_bg)
        details_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(details_container, text="Detailed Column Analysis", 
                font=("Arial", 12, "bold"), bg=self.light_bg, fg=self.primary_color).pack(anchor="w")
        
        self.details_text = tk.Text(
            details_container, height=20, font=("Consolas", 10), wrap="word",
            bg="#f8f9fa", padx=10, pady=10, fg=self.dark_text
        )
        self.details_text.pack(fill="both", expand=True, pady=(5, 0))

    def create_visualization_tab(self):
        """Create visualization tab"""
        self.plot_frame = tk.Frame(self.tab_vis, bg=self.light_bg)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_details(self):
        """Refresh detailed statistics for selected column"""
        if not hasattr(self, 'details_text') or self.df.empty or self.col_var.get() not in self.df.columns:
            return
            
        col = self.col_var.get()
        col_data = self.df[col]
        
        self.details_text.delete("1.0", tk.END)
        
        details = []
        details.append(f"📊 DETAILED STATISTICS FOR: {col}")
        details.append("=" * 50)
        details.append(f"Data Type: {col_data.dtype}")
        details.append(f"Total Values: {len(col_data):,}")
        details.append(f"Missing Values: {col_data.isnull().sum():,} ({col_data.isnull().mean()*100:.1f}%)")
        details.append(f"Unique Values: {col_data.nunique():,}")
        
        if col_data.dtype in ['int64', 'float64']:
            details.append("\nNUMERICAL STATISTICS:")
            details.append("-" * 30)
            details.append(f"Mean: {col_data.mean():.4f}")
            details.append(f"Median: {col_data.median():.4f}")
            details.append(f"Std Dev: {col_data.std():.4f}")
            details.append(f"Min: {col_data.min():.4f}")
            details.append(f"Max: {col_data.max():.4f}")
            details.append(f"Q1: {col_data.quantile(0.25):.4f}")
            details.append(f"Q3: {col_data.quantile(0.75):.4f}")
        else:
            details.append("\nCATEGORICAL STATISTICS:")
            details.append("-" * 30)
            value_counts = col_data.value_counts()
            if not value_counts.empty:
                details.append(f"Most Frequent: {value_counts.index[0]} (count: {value_counts.iloc[0]})")
                details.append("\nTOP 10 VALUES:")
                for i, (val, count) in enumerate(value_counts.head(10).items(), 1):
                    details.append(f"  {i}. {val}: {count} ({count/len(col_data)*100:.1f}%)")
        
        self.details_text.insert("1.0", "\n".join(details))

    def refresh_plot(self):
        """Refresh the plot for selected column"""
        if not hasattr(self, 'plot_frame') or self.df.empty or self.col_var.get() not in self.df.columns:
            return
            
        col = self.col_var.get()
        col_data = self.df[col]
        chart_type = self.chart_var.get()
        
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
        fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
        
        try:
            if chart_type == "auto":
                chart_type = "histogram" if col_data.dtype in ['int64', 'float64'] else "bar"
            
            if chart_type == "histogram" and col_data.dtype in ['int64', 'float64']:
                ax.hist(col_data.dropna(), bins=30, alpha=0.7, color=self.accent_color, edgecolor='black')
                ax.set_title(f'Histogram of {col}', fontsize=14, fontweight='bold')
                ax.set_xlabel(col)
                ax.set_ylabel('Frequency')
                
            elif chart_type == "boxplot" and col_data.dtype in ['int64', 'float64']:
                ax.boxplot(col_data.dropna())
                ax.set_title(f'Box Plot of {col}', fontsize=14, fontweight='bold')
                ax.set_ylabel(col)
                
            elif chart_type == "density" and col_data.dtype in ['int64', 'float64']:
                col_data.dropna().plot.density(ax=ax, color=self.accent_color, linewidth=2)
                ax.set_title(f'Density Plot of {col}', fontsize=14, fontweight='bold')
                
            elif chart_type == "bar":
                value_counts = col_data.value_counts().head(15)
                bars = ax.bar(range(len(value_counts)), value_counts.values, color=self.accent_color, alpha=0.7)
                ax.set_title(f'Bar Chart of {col}', fontsize=14, fontweight='bold')
                ax.set_xticks(range(len(value_counts)))
                ax.set_xticklabels([str(x) for x in value_counts.index], rotation=45, ha='right')
                
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            error_label = tk.Label(self.plot_frame, text=f"Error creating plot: {str(e)}", 
                                 fg=self.danger_color, bg=self.light_bg)
            error_label.pack(expand=True)

    def populate_overview_tree(self):
        """Populate the overview tree with column statistics"""
        if not hasattr(self, 'overview_tree') or self.df.empty:
            return
            
        self.overview_tree.delete(*self.overview_tree.get_children())
        
        for col in self.df.columns:
            s = self.df[col]
            dtype = str(s.dtype)
            missing = s.isnull().sum()
            missing_pct = (missing / len(s) * 100) if len(s) > 0 else 0
            unique = s.nunique(dropna=True)
            
            self.overview_tree.insert("", "end", values=(
                col, dtype, missing, f"{missing_pct:.1f}%", unique
            ))
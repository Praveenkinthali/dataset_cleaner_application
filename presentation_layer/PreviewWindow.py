# presentation_layer/PreviewWindow.py

import tkinter as tk
from tkinter import ttk
import pandas as pd

class PreviewWindow(tk.Frame):
    def __init__(self, master):
        self.light_bg = getattr(master, 'light_bg', '#f8f9fa')
        self.primary_color = getattr(master, 'primary_color', '#2c3e50')
        self.accent_color = getattr(master, 'accent_color', '#3498db')
        
        super().__init__(master, bg=self.light_bg)
        self.master = master
        
        self.page = 0
        self.rows_per_page = 100

        # Main container
        main_container = tk.Frame(self, bg=self.light_bg)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = tk.Frame(main_container, bg=self.light_bg)
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Button(header_frame, text="← Back to Main", bg="#95a5a6", fg="white",
                 command=lambda: master.show_frame(master.MainMenu),
                 font=("Arial", 10), padx=15).pack(side="left")

        title_frame = tk.Frame(header_frame, bg=self.light_bg)
        title_frame.pack(side="left", expand=True)
        
        tk.Label(title_frame, text="Dataset Preview", font=("Arial", 24, "bold"),
                fg=self.primary_color, bg=self.light_bg).pack()

        # Controls
        controls_frame = tk.LabelFrame(main_container, text="Preview Controls",
                                      font=("Arial", 11, "bold"), bg=self.light_bg)
        controls_frame.pack(fill="x", pady=(0, 15))

        mode_frame = tk.Frame(controls_frame, bg=self.light_bg)
        mode_frame.pack(fill="x", padx=10, pady=10)
        
        self.preview_mode = tk.StringVar(value="sample")
        tk.Radiobutton(mode_frame, text="📊 First 100 Rows", variable=self.preview_mode,
                      value="sample", command=self.reset_and_update, bg=self.light_bg).pack(side="left", padx=10)
        tk.Radiobutton(mode_frame, text="📜 Full Dataset (Paged)", variable=self.preview_mode,
                      value="full", command=self.reset_and_update, bg=self.light_bg).pack(side="left", padx=10)

        # Navigation
        nav_frame = tk.Frame(controls_frame, bg=self.light_bg)
        nav_frame.pack(fill="x", padx=10, pady=5)
        
        self.prev_btn = tk.Button(nav_frame, text="◀ Previous", command=self.prev_page,
                                  bg=self.accent_color, fg="white", width=15, state="disabled")
        self.prev_btn.pack(side="left", padx=5)
        
        self.next_btn = tk.Button(nav_frame, text="Next ▶", command=self.next_page,
                                  bg=self.accent_color, fg="white", width=15, state="disabled")
        self.next_btn.pack(side="left", padx=5)
        
        self.info_label = tk.Label(nav_frame, text="No dataset loaded", font=("Arial", 9), bg=self.light_bg)
        self.info_label.pack(side="right")

        # Table container
        table_container = tk.LabelFrame(main_container, text="Data Preview", font=("Arial", 11, "bold"),
                                       bg=self.light_bg)
        table_container.pack(fill="both", expand=True, pady=(0, 15))
        
        self.table_container = tk.Frame(table_container, bg=self.light_bg)
        self.table_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.update_table()

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

    def reset_and_update(self):
        self.page = 0
        self.update_table()

    def update_table(self):
        for widget in self.table_container.winfo_children():
            widget.destroy()

        # UPDATED: Use dataset_manager to get dataframe
        df = self.get_dataframe()
        
        if df is None or df.empty:
            tk.Label(self.table_container, text="No dataset loaded. Please upload a dataset.",
                    fg="#e74c3c", bg=self.light_bg, font=("Arial", 12), pady=50).pack(expand=True)
            self.info_label.config(text="No dataset available", fg="#e74c3c")
            self.update_navigation_buttons()
            return

        total_rows = len(df)
        total_cols = len(df.columns)
        self.info_label.config(text=f"Dataset: {total_rows:,} rows × {total_cols:,} columns", fg="#27ae60")

        if self.preview_mode.get() == "sample":
            display_df = df.head(100)
            self.display_table(display_df)
        else:
            start = self.page * self.rows_per_page
            end = min(start + self.rows_per_page, total_rows)
            display_df = df.iloc[start:end]
            
            total_pages = (total_rows - 1) // self.rows_per_page + 1
            page_info = f"Page {self.page + 1} of {total_pages}"
            tk.Label(self.table_container, text=page_info, fg=self.accent_color,
                    bg=self.light_bg, font=("Arial", 10, "bold")).pack()
            
            self.display_table(display_df)
        
        self.update_navigation_buttons()

    def display_table(self, df):
        tree = ttk.Treeview(self.table_container)
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="w")

        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        v_scroll = ttk.Scrollbar(self.table_container, orient="vertical", command=tree.yview)
        h_scroll = ttk.Scrollbar(self.table_container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

    def update_navigation_buttons(self):
        df = self.get_dataframe()
        if df is None or self.preview_mode.get() == "sample":
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            return

        total_pages = (len(df) - 1) // self.rows_per_page + 1
        
        if self.page > 0:
            self.prev_btn.config(state="normal")
        else:
            self.prev_btn.config(state="disabled")
        
        if self.page < total_pages - 1:
            self.next_btn.config(state="normal")
        else:
            self.next_btn.config(state="disabled")

    def next_page(self):
        df = self.get_dataframe()
        if df is not None and self.preview_mode.get() == "full":
            max_page = (len(df) - 1) // self.rows_per_page
            if self.page < max_page:
                self.page += 1
                self.update_table()

    def prev_page(self):
        if self.preview_mode.get() == "full" and self.page > 0:
            self.page -= 1
            self.update_table()
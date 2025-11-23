# presentation_layer/CleaningWindow.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd

class CleaningWindow(tk.Frame):
    """
    Presentation Layer - Data Cleaning UI
    Delegates ALL operations to DataCleaningController
    """
    
    def __init__(self, master):
        # Initialize colors with defaults in case master doesn't have them
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
        
        # Access the controller from master
        self.cleaning_controller = master.cleaning_controller
        
        # Main container with better organization
        main_container = tk.Frame(self, bg=self.light_bg)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with back button
        header_frame = tk.Frame(main_container, bg=self.light_bg)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Back button on left
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

        # Title in center
        title_frame = tk.Frame(header_frame, bg=self.light_bg)
        title_frame.pack(side="left", expand=True)
        
        tk.Label(
            title_frame, 
            text="Data Cleaning Studio", 
            font=("Arial", 24, "bold"), 
            fg=self.primary_color,
            bg=self.light_bg
        ).pack()
        
        tk.Label(
            title_frame, 
            text="Automated and manual data cleaning tools", 
            font=("Arial", 11), 
            fg=self.light_text,
            bg=self.light_bg
        ).pack()

        # Action buttons frame
        action_frame = tk.LabelFrame(
            main_container, 
            text="Cleaning Actions",
            font=("Arial", 12, "bold"),
            fg=self.primary_color,
            bg=self.light_bg,
            relief="groove",
            bd=1
        )
        action_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        btn_frame = tk.Frame(action_frame, bg=self.light_bg)
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame, 
            text="🤖 Auto Clean", 
            command=self.auto_clean, 
            width=15, 
            bg=self.success_color, 
            fg="white",
            font=("Arial", 11, "bold"),
            height=2
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame, 
            text="🔧 Manual Clean", 
            command=self.manual_clean_window,
            width=15, 
            bg=self.accent_color, 
            fg="white",
            font=("Arial", 11, "bold"),
            height=2
        ).pack(side="left", padx=10)

        # Summary section
        summary_label = tk.Label(
            main_container, 
            text="📊 Dataset Quality Summary", 
            font=("Arial", 14, "bold"),
            fg=self.primary_color,
            bg=self.light_bg
        )
        summary_label.pack(pady=(10, 5), anchor="w")
        
        self.summary_container = tk.Frame(main_container, bg=self.light_bg)
        self.summary_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.update_summary()

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

    def auto_clean(self):
        """Auto Clean - Delegates to DataCleaningController"""
        result = self.cleaning_controller.auto_clean(self.master.dataset_id)
        
        if not result["success"]:
            messagebox.showerror("Error", result["message"])
            return
        
        # Update UI
        self.update_summary()
        
        # Show success message with improved formatting
        messagebox.showinfo(
            "✅ Auto Clean Completed", 
            f"Dataset cleaned successfully using intelligent automation!\n\n"
            f"📈 **Before Cleaning:**\n"
            f"   • Rows: {result['original_shape'][0]:,}\n"
            f"   • Columns: {result['original_shape'][1]:,}\n\n"
            f"📊 **After Cleaning:**\n"
            f"   • Rows: {result['new_shape'][0]:,}\n"
            f"   • Columns: {result['new_shape'][1]:,}\n\n"
            f"🎯 **Changes Made:**\n"
            f"   • Duplicates removed: {result['duplicates_removed']:,}\n"
            f"   • Columns removed: {result['columns_removed']:,}\n"
            f"   • Missing values handled automatically"
        )
    
    def manual_clean_window(self):
        """Manual Clean Window - UI for manual cleaning operations with improved GUI"""
        df = self.get_dataframe()
        
        if df is None or df.empty:
            messagebox.showerror("Error", "No dataset loaded or dataset is empty.")
            return

        # Create manual cleaning window
        manual_win = tk.Toplevel(self)
        manual_win.title("🔧 Manual Data Cleaning")
        manual_win.geometry("1000x700")
        manual_win.minsize(900, 600)
        manual_win.configure(bg=self.light_bg)

        # Header
        header_frame = tk.Frame(manual_win, bg=self.light_bg)
        header_frame.pack(fill="x", padx=20, pady=15)
        
        tk.Label(
            header_frame, 
            text="🔧 Manual Data Cleaning", 
            font=("Arial", 20, "bold"),
            fg=self.primary_color,
            bg=self.light_bg
        ).pack()
        
        tk.Label(
            header_frame, 
            text="Edit and fix missing or problematic values in your dataset",
            font=("Arial", 11),
            fg=self.light_text,
            bg=self.light_bg
        ).pack()

        # Status bar
        status_var = tk.StringVar(value="🟢 Ready to clean data")
        status_bar = tk.Label(
            manual_win, 
            textvariable=status_var, 
            relief="sunken", 
            anchor="w", 
            bg="#ecf0f1",
            font=("Arial", 9),
            fg=self.dark_text
        )
        status_bar.pack(fill="x", side="bottom", padx=10, pady=5)
        
        def update_status(message):
            status_var.set(message)
            manual_win.update_idletasks()

        # Control panel
        control_panel = tk.LabelFrame(
            manual_win,
            text="Cleaning Tools",
            font=("Arial", 11, "bold"),
            fg=self.primary_color,
            bg=self.light_bg,
            relief="groove",
            bd=1
        )
        control_panel.pack(fill="x", padx=15, pady=10)

        # Column selection frame
        col_frame = tk.Frame(control_panel, bg=self.light_bg)
        col_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            col_frame, 
            text="📋 Select Column:", 
            font=("Arial", 10, "bold"),
            bg=self.light_bg,
            fg=self.dark_text
        ).pack(side="left", padx=5)

        col_var = tk.StringVar()
        
        def get_col_choices():
            df_current = self.get_dataframe()
            if df_current is None or df_current.empty:
                return []
            choices = []
            for col in df_current.columns:
                missing_pct = (df_current[col].isnull().mean() * 100)
                dtype = df_current[col].dtype
                choices.append(f"{col} ({dtype}) - {missing_pct:.1f}% missing")
            return choices

        col_dropdown = ttk.Combobox(
            col_frame, 
            textvariable=col_var, 
            values=get_col_choices(), 
            state="readonly", 
            width=60,
            font=("Arial", 9)
        )
        col_dropdown.pack(side="left", padx=10)
        
        def get_selected_column():
            if not col_var.get():
                return None
            # Extract column name from the display string
            return col_var.get().split(" (")[0]

        # Operations frame
        ops_frame = tk.Frame(control_panel, bg=self.light_bg)
        ops_frame.pack(fill="x", padx=10, pady=10)

        # Operation functions
        def fill_mean():
            col = get_selected_column()
            if not col:
                update_status("❌ Please select a column first")
                return
            
            result = self.cleaning_controller.fill_missing_with_mean(col, self.master.dataset_id)
            
            if result["success"]:
                update_status(f"✅ Filled missing values in '{col}' with mean: {result['mean_value']:.2f}")
                refresh_display()
            else:
                update_status(f"❌ {result['message']}")

        def fill_mode():
            col = get_selected_column()
            if not col:
                update_status("❌ Please select a column first")
                return
            
            result = self.cleaning_controller.fill_missing_with_mode(col, self.master.dataset_id)
            
            if result["success"]:
                update_status(f"✅ Filled missing values in '{col}' with mode: {result['mode_value']}")
                refresh_display()
            else:
                update_status(f"❌ {result['message']}")

        def fill_custom():
            col = get_selected_column()
            if not col:
                update_status("❌ Please select a column first")
                return
            
            current_dtype = self.get_dataframe()[col].dtype
            val = simpledialog.askstring(
                "Fill Custom Value", 
                f"Enter value for '{col}' (dtype: {current_dtype}):",
                parent=manual_win
            )
            if val is not None:
                result = self.cleaning_controller.fill_missing_with_custom(col, val, self.master.dataset_id)
                
                if result["success"]:
                    update_status(f"✅ Filled missing values in '{col}' with: {result['custom_value']}")
                    refresh_display()
                else:
                    update_status(f"❌ {result['message']}")

        def drop_col():
            col = get_selected_column()
            if not col:
                update_status("❌ Please select a column first")
                return
            
            if messagebox.askyesno(
                "⚠️ Confirm Drop", 
                f"Are you sure you want to drop column '{col}'?\n\nThis action cannot be undone.",
                parent=manual_win
            ):
                result = self.cleaning_controller.drop_column(col, self.master.dataset_id)
                
                if result["success"]:
                    update_status(f"🗑️ Dropped column: {col}")
                    # Refresh column dropdown
                    refresh_display()
                    # Force focus back to manual cleaning window
                    manual_win.focus_force()
                    manual_win.lift()
                else:
                    update_status(f"❌ {result['message']}")

        # Operation buttons with colors
        button_configs = [
            ("📊 Fill with Mean", fill_mean, self.success_color),
            ("📈 Fill with Mode", fill_mode, self.accent_color),
            ("✏️ Fill Custom", fill_custom, "#f39c12"),
            ("🗑️ Drop Column", drop_col, self.danger_color)
        ]

        for text, command, color in button_configs:
            btn = tk.Button(
                ops_frame, 
                text=text, 
                command=command,
                width=14, 
                bg=color,
                fg="white",
                font=("Arial", 9, "bold"),
                relief="raised"
            )
            btn.pack(side="left", padx=5)

        # Data preview frame
        preview_frame = tk.LabelFrame(
            manual_win,
            text="🔍 Problematic Rows Preview",
            font=("Arial", 11, "bold"),
            fg=self.primary_color,
            bg=self.light_bg,
            relief="groove",
            bd=1
        )
        preview_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Create treeview with scrollbars
        tree_container = tk.Frame(preview_frame, bg=self.light_bg)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Configure treeview style with visible columns
        style = ttk.Style()
        style.theme_use('clam')  # Use 'clam' theme for better control over colors
        
        # Configure Treeview colors
        style.configure("Treeview", 
                       background="#ffffff",
                       foreground=self.dark_text,
                       rowheight=25,
                       fieldbackground="#ffffff",
                       borderwidth=1)
        
        # Configure Treeview Heading with visible background and text
        style.configure("Treeview.Heading", 
                       background="#2c3e50",  # Dark blue background
                       foreground="white",     # White text
                       font=("Arial", 10, "bold"),
                       relief="flat",
                       padding=(5, 5))
        
        # Map the heading style for hover effects
        style.map("Treeview.Heading",
                 background=[('active', '#34495e')])  # Slightly lighter on hover

        tree = ttk.Treeview(tree_container, show="headings", selectmode="extended", style="Treeview")
        
        v_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

        def get_problem_rows():
            """Find rows with missing values or problematic patterns"""
            df_current = self.get_dataframe()
            if df_current is None or df_current.empty:
                return pd.DataFrame()
            
            # Find rows with NaN values
            nan_mask = df_current.isnull().any(axis=1)
            
            # Find rows with question marks in string columns
            question_mask = pd.Series(False, index=df_current.index)
            for col in df_current.select_dtypes(include=['object']).columns:
                question_mask = question_mask | df_current[col].astype(str).str.contains(r'\?', regex=True, na=False)
            
            return df_current[nan_mask | question_mask]

        def refresh_display():
            """Refresh the preview display"""
            df_current = self.get_dataframe()
            tree.delete(*tree.get_children())
            
            if df_current.empty:
                return
            
            tree["columns"] = list(df_current.columns)
            for col in df_current.columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="w", minwidth=100)
            
            # Show problematic rows
            problem_rows = get_problem_rows()
            for idx, row in problem_rows.iterrows():
                values = [row[col] if pd.notna(row[col]) else "❌ MISSING" for col in df_current.columns]
                tree.insert("", "end", iid=str(idx), values=values)
            
            # Update column dropdown
            col_dropdown['values'] = get_col_choices()
            if not col_var.get() and df_current.columns.any():
                col_var.set(get_col_choices()[0])
            
            update_status(f"👀 Showing {len(problem_rows)} problematic rows out of {len(df_current)} total rows")

        # Initial display
        refresh_display()

        # Action buttons frame
        action_frame = tk.Frame(manual_win, bg=self.light_bg)
        action_frame.pack(fill="x", padx=15, pady=15)

        def finish():
            self.update_summary()
            manual_win.destroy()
            messagebox.showinfo("✅ Success", "All cleaning changes applied to dataset!")

        def cancel():
            if messagebox.askyesno(
                "❌ Discard Changes", 
                "Discard all unsaved cleaning changes?",
                parent=manual_win
            ):
                manual_win.destroy()

        tk.Button(
            action_frame, 
            text="💾 Apply & Close", 
            command=finish,
            bg=self.success_color, 
            fg="white", 
            width=15,
            font=("Arial", 10, "bold"),
            height=1
        ).pack(side="right", padx=10)
        
        tk.Button(
            action_frame, 
            text="❌ Cancel", 
            command=cancel,
            bg=self.danger_color, 
            fg="white", 
            width=15,
            font=("Arial", 10, "bold"),
            height=1
        ).pack(side="right", padx=5)

    def update_summary(self):
        """Update the quality summary display with improved GUI"""
        for widget in self.summary_container.winfo_children():
            widget.destroy()

        # Get quality summary from controller
        summary = self.cleaning_controller.get_data_quality_summary()
        
        if summary is None:
            no_data_label = tk.Label(
                self.summary_container, 
                text="📭 No dataset loaded. Please upload a dataset to begin cleaning.", 
                fg=self.light_text, 
                font=("Arial", 11),
                bg=self.light_bg,
                pady=20
            )
            no_data_label.pack(fill="both", expand=True)
            return

        # Create summary cards
        cards_frame = tk.Frame(self.summary_container, bg=self.light_bg)
        cards_frame.pack(fill="x", pady=5)

        cards_data = [
            ("📊 Dataset Shape", f"{summary['total_rows']:,} × {summary['total_cols']:,}", "#3498db"),
            ("❌ Missing Values", f"{summary['missing_total']:,} ({summary['missing_pct']:.1f}%)", 
             "#e74c3c" if summary['missing_total'] > 0 else "#27ae60"),
            ("🔄 Duplicates", f"{summary['duplicate_count']:,}", 
             "#f39c12" if summary['duplicate_count'] > 0 else "#27ae60"),
            ("💾 Memory Usage", f"{summary['memory_usage_mb']:.1f} MB", "#9b59b6")
        ]

        for i, (title, value, color) in enumerate(cards_data):
            card = self.create_summary_card(cards_frame, title, value, color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            cards_frame.columnconfigure(i, weight=1)

        # Detailed missing values table
        df = self.get_dataframe()
        if not df.empty:
            detail_frame = tk.LabelFrame(
                self.summary_container,
                text="📋 Column-wise Missing Values",
                font=("Arial", 11, "bold"),
                fg=self.primary_color,
                bg=self.light_bg,
                relief="groove",
                bd=1
            )
            detail_frame.pack(fill="x", pady=10)

            missing_details = df.isnull().sum()
            missing_pct = (df.isnull().mean() * 100).round(2)
            
            # Configure treeview style for summary table with visible columns
            summary_style = ttk.Style()
            summary_style.theme_use('clam')
            
            # Configure Treeview colors for summary table
            summary_style.configure("Summary.Treeview", 
                                  background="#ffffff",
                                  foreground=self.dark_text,
                                  rowheight=25,
                                  fieldbackground="#ffffff",
                                  borderwidth=1)
            
            # Configure Treeview Heading for summary table with visible background and text
            summary_style.configure("Summary.Treeview.Heading", 
                                  background="#2c3e50",  # Dark blue background
                                  foreground="white",     # White text
                                  font=("Arial", 10, "bold"),
                                  relief="flat",
                                  padding=(5, 5))
            
            # Create treeview for detailed summary with custom style
            detail_tree = ttk.Treeview(
                detail_frame,
                columns=("Column", "Data Type", "Missing", "Missing %"),
                show="headings",
                height=min(len(df.columns), 8),
                style="Summary.Treeview"
            )
            
            # Configure columns with visible headers
            detail_tree.heading("Column", text="📋 Column")
            detail_tree.heading("Data Type", text="🔧 Data Type")
            detail_tree.heading("Missing", text="❌ Missing Values")
            detail_tree.heading("Missing %", text="📊 Missing %")
            
            detail_tree.column("Column", width=200)
            detail_tree.column("Data Type", width=120)
            detail_tree.column("Missing", width=120)
            detail_tree.column("Missing %", width=100)
            
            # Add data
            for col in df.columns:
                dtype = str(df[col].dtype)
                missing_val = missing_details[col]
                missing_percent = missing_pct[col]
                
                detail_tree.insert("", "end", values=(col, dtype, missing_val, f"{missing_percent}%"))
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(detail_frame, orient="vertical", command=detail_tree.yview)
            detail_tree.configure(yscrollcommand=scrollbar.set)
            
            detail_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y")

    def create_summary_card(self, parent, title, value, color):
        """Create a summary card widget"""
        card = tk.Frame(parent, relief="raised", borderwidth=1, bg="white")
        
        tk.Label(card, text=title, font=("Arial", 10, "bold"), 
                bg="white", fg="#7f8c8d").pack(pady=(10, 5))
        tk.Label(card, text=value, font=("Arial", 14, "bold"), 
                bg="white", fg=color).pack(pady=(5, 10))
        
        return card
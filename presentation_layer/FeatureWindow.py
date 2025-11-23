# presentation_layer/FeatureWindow.py

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import pandas as pd
import numpy as np

class FeatureWindow(tk.Frame):
    """
    Presentation Layer - Feature Engineering UI
    Delegates ALL operations to FeatureEngineeringController
    """
    
    def __init__(self, master):
        # Initialize colors
        self.light_bg = getattr(master, 'light_bg', '#f8f9fa')
        self.primary_color = getattr(master, 'primary_color', '#2c3e50')
        self.accent_color = getattr(master, 'accent_color', '#3498db')
        self.success_color = getattr(master, 'success_color', '#27ae60')
        self.danger_color = getattr(master, 'danger_color', '#e74c3c')
        
        super().__init__(master, bg=self.light_bg)
        self.master = master
        
        # Access controller from master (3-tier architecture)
        self.feature_controller = master.feature_controller
        self.dataset_manager = master.dataset_manager
        
        self.status_var = tk.StringVar(value="Loading...")

        # Main container
        main_container = tk.Frame(self, bg=self.light_bg)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header with back button
        header_frame = tk.Frame(main_container, bg=self.light_bg)
        header_frame.pack(fill="x", pady=(0, 10))
        
        tk.Button(header_frame, text="← Back", 
                 command=lambda: master.show_frame(master.MainMenu),
                 bg="#95a5a6", fg="white", padx=15).pack(side="left")

        tk.Label(header_frame, text="Feature Engineering Studio", 
                font=("Arial", 20, "bold"), fg=self.primary_color, 
                bg=self.light_bg).pack(side="left", padx=20)

        # Control panel
        control_frame = tk.Frame(main_container, bg=self.light_bg)
        control_frame.pack(fill="x", pady=10)
        
        tk.Button(control_frame, text="↶ Undo", command=self.undo, 
                 width=8, bg=self.accent_color, fg="white").pack(side="left", padx=2)
        tk.Button(control_frame, text="↷ Redo", command=self.redo,
                 width=8, bg=self.accent_color, fg="white").pack(side="left", padx=2)

        # Status bar
        tk.Label(main_container, textvariable=self.status_var, 
                relief="sunken", anchor="w", bg="#ecf0f1").pack(fill="x", side="bottom")

        # Create tabs
        self.create_tabs(main_container)
        self.refresh_all()

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

    def create_tabs(self, parent):
        """Create the tabbed interface"""
        self.tabs = ttk.Notebook(parent)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=8)

        # Numerical Features Tab
        self.tab_numerical = tk.Frame(self.tabs, bg=self.light_bg)
        self.tabs.add(self.tab_numerical, text="🔢 Numerical")
        self.create_numerical_tab()

        # Categorical Features Tab
        self.tab_categorical = tk.Frame(self.tabs, bg=self.light_bg)
        self.tabs.add(self.tab_categorical, text="🏷️ Categorical")
        self.create_categorical_tab()

        # Advanced Tab
        self.tab_advanced = tk.Frame(self.tabs, bg=self.light_bg)
        self.tabs.add(self.tab_advanced, text="⚙️ Advanced")
        self.create_advanced_tab()

    def create_numerical_tab(self):
        """Create numerical transformations tab"""
        col_frame = tk.Frame(self.tab_numerical, bg=self.light_bg)
        col_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(col_frame, text="Select Column:", font=("Arial", 11, "bold"), 
                bg=self.light_bg).pack(side="left", padx=10)
        
        self.num_col_var = tk.StringVar()
        self.num_combo = ttk.Combobox(col_frame, textvariable=self.num_col_var, 
                                     state="readonly", width=25)
        self.num_combo.pack(side="left", padx=5)

        trans_frame = tk.LabelFrame(self.tab_numerical, text="Transformations", 
                                   font=("Arial", 10, "bold"), bg=self.light_bg)
        trans_frame.pack(fill="x", padx=10, pady=10)

        # Scaling
        row1 = tk.Frame(trans_frame, bg=self.light_bg)
        row1.pack(fill="x", pady=2)
        
        tk.Button(row1, text="Standardize (Z-score)", command=self.standardize,
                 width=18, bg=self.accent_color, fg="white").pack(side="left", padx=2)
        tk.Button(row1, text="Normalize (0-1)", command=self.minmax_scale,
                 width=15, bg=self.accent_color, fg="white").pack(side="left", padx=2)
        tk.Button(row1, text="Robust Scale", command=self.robust_scale,
                 width=15, bg=self.accent_color, fg="white").pack(side="left", padx=2)

        # Transformations
        row2 = tk.Frame(trans_frame, bg=self.light_bg)
        row2.pack(fill="x", pady=2)
        
        tk.Button(row2, text="Log Transform", command=self.log_transform,
                 width=15, bg=self.danger_color, fg="white").pack(side="left", padx=2)
        tk.Button(row2, text="Square Root", command=self.sqrt_transform,
                 width=15, bg=self.danger_color, fg="white").pack(side="left", padx=2)
        tk.Button(row2, text="Bin Data", command=self.bin_data,
                 width=15, bg=self.success_color, fg="white").pack(side="left", padx=2)

        # Advanced
        row3 = tk.Frame(trans_frame, bg=self.light_bg)
        row3.pack(fill="x", pady=2)
        
        tk.Button(row3, text="Polynomial Features", command=self.polynomial_features,
                 width=18, bg=self.success_color, fg="white").pack(side="left", padx=2)

    def create_categorical_tab(self):
        """Create categorical transformations tab"""
        col_frame = tk.Frame(self.tab_categorical, bg=self.light_bg)
        col_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(col_frame, text="Select Column:", font=("Arial", 11, "bold"), 
                bg=self.light_bg).pack(side="left", padx=10)
        
        self.cat_col_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(col_frame, textvariable=self.cat_col_var, 
                                     state="readonly", width=25)
        self.cat_combo.pack(side="left", padx=5)

        encoding_frame = tk.LabelFrame(self.tab_categorical, text="Encoding Methods", 
                                      font=("Arial", 10, "bold"), bg=self.light_bg)
        encoding_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(encoding_frame, text="One-Hot Encode", command=self.one_hot_encode,
                 width=15, bg="#9b59b6", fg="white").pack(side="left", padx=5, pady=5)
        tk.Button(encoding_frame, text="Label Encode", command=self.label_encode,
                 width=15, bg="#9b59b6", fg="white").pack(side="left", padx=5, pady=5)

    def create_advanced_tab(self):
        """Create advanced features tab"""
        # PCA
        pca_frame = tk.LabelFrame(self.tab_advanced, text="Dimensionality Reduction (PCA)", 
                                 font=("Arial", 11, "bold"), bg=self.light_bg)
        pca_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(pca_frame, text="Number of Components:", bg=self.light_bg).pack(side="left", padx=5)
        self.pca_components_var = tk.StringVar(value="2")
        tk.Entry(pca_frame, textvariable=self.pca_components_var, width=5).pack(side="left", padx=5)
        tk.Button(pca_frame, text="Apply PCA", command=self.apply_pca,
                 bg=self.danger_color, fg="white").pack(side="left", padx=10)

        # Custom feature
        custom_frame = tk.LabelFrame(self.tab_advanced, text="Custom Feature Expression", 
                                    font=("Arial", 11, "bold"), bg=self.light_bg)
        custom_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(custom_frame, text="Feature Name:", bg=self.light_bg).pack(anchor="w", padx=10)
        self.custom_name_var = tk.StringVar()
        tk.Entry(custom_frame, textvariable=self.custom_name_var, width=30).pack(padx=10, pady=2)

        tk.Label(custom_frame, text="Expression (e.g., df['col1'] + df['col2']):", 
                bg=self.light_bg).pack(anchor="w", padx=10)
        self.custom_expr_var = tk.StringVar()
        tk.Entry(custom_frame, textvariable=self.custom_expr_var, width=50).pack(padx=10, pady=2)

        tk.Button(custom_frame, text="Create Feature", command=self.create_custom_feature,
                 bg=self.success_color, fg="white").pack(pady=10)

    # ========== TRANSFORMATION METHODS (All delegate to controller) ==========

    def standardize(self):
        col = self.num_col_var.get()
        if not col:
            self.show_error("Please select a column")
            return
        result = self.feature_controller.standardize_column(col, self.master.dataset_id)
        self.handle_result(result)

    def minmax_scale(self):
        col = self.num_col_var.get()
        if not col:
            self.show_error("Please select a column")
            return
        result = self.feature_controller.minmax_scale_column(col, self.master.dataset_id)
        self.handle_result(result)

    def robust_scale(self):
        col = self.num_col_var.get()
        if not col:
            self.show_error("Please select a column")
            return
        result = self.feature_controller.robust_scale_column(col, self.master.dataset_id)
        self.handle_result(result)

    def log_transform(self):
        col = self.num_col_var.get()
        if not col:
            self.show_error("Please select a column")
            return
        result = self.feature_controller.log_transform_column(col, self.master.dataset_id)
        self.handle_result(result)

    def sqrt_transform(self):
        col = self.num_col_var.get()
        if not col:
            self.show_error("Please select a column")
            return
        result = self.feature_controller.sqrt_transform_column(col, self.master.dataset_id)
        self.handle_result(result)

    def bin_data(self):
        col = self.num_col_var.get()
        if not col:
            self.show_error("Please select a column")
            return
        bins = simpledialog.askinteger("Bin Data", "Number of bins:", 
                                      initialvalue=5, minvalue=2, maxvalue=50)
        if not bins:
            return
        result = self.feature_controller.bin_column(col, bins, self.master.dataset_id)
        self.handle_result(result)

    def polynomial_features(self):
        col = self.num_col_var.get()
        if not col:
            self.show_error("Please select a column")
            return
        degree = simpledialog.askinteger("Polynomial Features", "Degree:", 
                                        initialvalue=2, minvalue=2, maxvalue=5)
        if not degree:
            return
        result = self.feature_controller.create_polynomial_features(col, degree, self.master.dataset_id)
        self.handle_result(result)

    def one_hot_encode(self):
        col = self.cat_col_var.get()
        if not col:
            self.show_error("Please select a column")
            return
        result = self.feature_controller.one_hot_encode_column(col, self.master.dataset_id)
        self.handle_result(result)

    def label_encode(self):
        col = self.cat_col_var.get()
        if not col:
            self.show_error("Please select a column")
            return
        result = self.feature_controller.label_encode_column(col, self.master.dataset_id)
        self.handle_result(result)

    def apply_pca(self):
        try:
            n_components = int(self.pca_components_var.get())
        except ValueError:
            self.show_error("Invalid number of components")
            return
        result = self.feature_controller.apply_pca(n_components, self.master.dataset_id)
        self.handle_result(result)

    def create_custom_feature(self):
        name = self.custom_name_var.get()
        expr = self.custom_expr_var.get()
        if not name or not expr:
            self.show_error("Please enter feature name and expression")
            return
        result = self.feature_controller.create_custom_feature(name, expr, self.master.dataset_id)
        self.handle_result(result)

    def undo(self):
        result = self.feature_controller.undo()
        self.handle_result(result)

    def redo(self):
        result = self.feature_controller.redo()
        self.handle_result(result)

    # ========== UI HELPER METHODS ==========

    def handle_result(self, result):
        """Handle controller result and update UI"""
        if result["success"]:
            messagebox.showinfo("✅ Success", result["message"])
            self.refresh_all()
        else:
            messagebox.showerror("❌ Error", result["message"])
        self.status_var.set(result["message"])

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.status_var.set(f"❌ Error: {message}")

    def refresh_all(self):
        """Refresh UI components"""
        df = self.get_dataframe()
        
        if df is None or df.empty:
            self.status_var.set("No dataset loaded")
            return
        
        # Update dropdowns
        numeric_cols = list(df.select_dtypes(include=['int64', 'float64']).columns)
        categorical_cols = list(df.select_dtypes(include=['object']).columns)
        
        self.num_combo['values'] = numeric_cols
        if numeric_cols:
            self.num_col_var.set(numeric_cols[0])
        
        self.cat_combo['values'] = categorical_cols
        if categorical_cols:
            self.cat_col_var.set(categorical_cols[0])
        
        self.status_var.set(f"Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
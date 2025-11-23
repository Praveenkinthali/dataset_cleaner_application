# simple_main.py - GUARANTEED TO WORK
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

class SimpleDatasetCleaner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Dataset Cleaner")
        self.geometry("800x600")
        
        # Current dataset
        self.df = None
        self.file_path = None
        
        self.create_ui()
        
    def create_ui(self):
        # Main container
        main_frame = tk.Frame(self, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="📊 Simple Dataset Cleaner", 
                              font=("Arial", 24, "bold"), bg='#f0f0f0')
        title_label.pack(pady=20)
        
        # Upload button
        upload_btn = tk.Button(main_frame, text="📤 Upload Dataset", 
                              command=self.upload_dataset,
                              bg='#3498db', fg='white', font=("Arial", 14),
                              width=20, height=2)
        upload_btn.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="No dataset loaded", 
                                    font=("Arial", 12), bg='#f0f0f0')
        self.status_label.pack(pady=10)
        
        # Preview frame
        preview_frame = tk.LabelFrame(main_frame, text="Data Preview", 
                                     font=("Arial", 12, "bold"))
        preview_frame.pack(fill='both', expand=True, pady=20)
        
        # Treeview for data
        self.tree = ttk.Treeview(preview_frame)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')
        
        # Control buttons
        control_frame = tk.Frame(main_frame, bg='#f0f0f0')
        control_frame.pack(pady=10)
        
        clean_btn = tk.Button(control_frame, text="🧹 Clean Data", 
                             command=self.clean_data, bg='#27ae60', fg='white')
        clean_btn.pack(side='left', padx=5)
        
        stats_btn = tk.Button(control_frame, text="📈 Show Stats", 
                             command=self.show_stats, bg='#9b59b6', fg='white')
        stats_btn.pack(side='left', padx=5)
        
        export_btn = tk.Button(control_frame, text="💾 Export", 
                              command=self.export_data, bg='#e74c3c', fg='white')
        export_btn.pack(side='left', padx=5)
    
    def upload_dataset(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
                
            self.file_path = file_path
            self.update_preview()
            self.status_label.config(text=f"Loaded: {os.path.basename(file_path)} - {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def update_preview(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if self.df is None:
            return
            
        # Set up columns
        self.tree["columns"] = list(self.df.columns)
        self.tree["show"] = "headings"
        
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Add data (first 50 rows)
        for _, row in self.df.head(50).iterrows():
            self.tree.insert("", "end", values=list(row))
    
    def clean_data(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No dataset loaded")
            return
            
        try:
            # Simple cleaning
            original_shape = self.df.shape
            
            # Remove duplicates
            self.df = self.df.drop_duplicates()
            
            # Fill missing values
            for col in self.df.columns:
                if self.df[col].dtype in ['int64', 'float64']:
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                else:
                    self.df[col].fillna('Unknown', inplace=True)
            
            self.update_preview()
            
            messagebox.showinfo("Success", 
                              f"Data cleaned!\n"
                              f"Duplicates removed: {original_shape[0] - self.df.shape[0]}\n"
                              f"New shape: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            
        except Exception as e:
            messagebox.showerror("Error", f"Cleaning failed:\n{str(e)}")
    
    def show_stats(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No dataset loaded")
            return
            
        stats_text = f"Dataset Statistics:\n\n"
        stats_text += f"Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns\n"
        stats_text += f"Memory: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n"
        stats_text += f"Missing values: {self.df.isnull().sum().sum()}\n"
        stats_text += f"Duplicates: {self.df.duplicated().sum()}\n\n"
        
        stats_text += "Column types:\n"
        for col, dtype in self.df.dtypes.items():
            stats_text += f"  {col}: {dtype}\n"
        
        messagebox.showinfo("Dataset Statistics", stats_text)
    
    def export_data(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No dataset to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.csv'):
                self.df.to_csv(file_path, index=False)
            else:
                self.df.to_excel(file_path, index=False)
                
            messagebox.showinfo("Success", f"Dataset exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")

if __name__ == "__main__":
    print("Starting Simple Dataset Cleaner...")
    app = SimpleDatasetCleaner()
    app.mainloop()
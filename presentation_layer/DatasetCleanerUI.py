# presentation_layer/DatasetCleanerUI.py - SIMPLE STYLING

import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Business Layer Controllers
from business_layer.DataCleaningController import DataCleaningController
from business_layer.FeatureEngineeringController import FeatureEngineeringController
from business_layer.ExportController import ExportController
from business_layer.LoggingService import LoggingService

# Import Data Layer
from data_layer.DatabaseManager import DatabaseManager
from data_layer.DatasetManager import DatasetManager
from data_layer.FileHandler import FileHandler

# Import models
from models import Dataset

# Import UI Windows
from .PreviewWindow import PreviewWindow
from .CleaningWindow import CleaningWindow
from .FeatureWindow import FeatureWindow
from .StatsWindow import StatsWindow
from .VisualizeWindow import VisualizeWindow
from .LogsWindow import LogsWindow


class DatasetCleanerUI(tk.Tk):
    """
    Main Presentation Layer Class - Simple Style (matching main_window.py)
    """
    
    def __init__(self):
        super().__init__()
        
        # Simple Color Scheme matching main_window.py
        self.light_bg = '#f8f9fa'
        self.primary_color = '#2c3e50'
        self.secondary_color = '#34495e'
        self.accent_color = '#3498db'
        self.success_color = '#27ae60'
        self.danger_color = '#e74c3c'
        self.light_text = '#7f8c8d'
        self.dark_text = '#2c3e50'
        
        # Configure main window
        self.title("Dataset Cleaner Application")
        self.geometry("900x600")
        self.configure(bg=self.light_bg)
        
        # Initialize Data Layer
        try:
            self.db_manager = DatabaseManager(
                host='localhost',
                user='root',
                password='2511',
                database='dataset_cleaner',
                port=3306
            )
            connection_success = self.db_manager.connect()
            if not connection_success:
                # Silent fallback to mock manager without console output
                self.db_manager = self._create_mock_db_manager()
        except Exception:
            # Silent fallback to mock manager without console output
            self.db_manager = self._create_mock_db_manager()
        
        self.dataset_manager = DatasetManager()
        self.file_handler = FileHandler()
        
        # Initialize Business Layer
        self.logging_service = LoggingService(self.db_manager)
        self.cleaning_controller = DataCleaningController(self.dataset_manager, self.logging_service)
        self.feature_controller = FeatureEngineeringController(self.dataset_manager, self.logging_service)
        self.export_controller = ExportController(self.file_handler, self.db_manager, self.logging_service)
        
        # Current dataset tracking
        self.dataset_id = None
        
        # Presentation Layer frames
        self.frames = {}
        self.MainMenu = MainMenu
        
        # Show main menu
        self.show_frame(MainMenu)
    
    def _create_mock_db_manager(self):
        """Create a mock database manager for when database is unavailable"""
        class MockDBManager:
            def insert_dataset(self, *args):
                return 1
            def insert_log(self, *args):
                return None
            def fetch_logs(self, *args):
                return []
            def disconnect(self):
                return None
            def test_connection(self):
                return {"connected": False}
        return MockDBManager()
    
    def show_frame(self, frame_class):
        """Show the specified frame, creating it if needed"""
        # Recreate certain windows to reset state
        if frame_class in [PreviewWindow] and frame_class in self.frames:
            self.frames[frame_class].destroy()
            del self.frames[frame_class]
        
        # Hide all current frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Create frame if it doesn't exist
        if frame_class not in self.frames:
            frame = frame_class(self)
            self.frames[frame_class] = frame
            frame.pack(fill="both", expand=True)
        else:
            self.frames[frame_class].pack(fill="both", expand=True)
        
        # Auto-refresh logs window
        if frame_class == LogsWindow and hasattr(self.frames[frame_class], 'on_show'):
            self.frames[frame_class].on_show()
    
    def upload_dataset(self):
        """Upload dataset"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            # Use FileHandler to load file
            result = self.file_handler.load_file(file_path)
            
            if not result["success"]:
                messagebox.showerror("Upload Error", result["message"])
                return
            
            # Create Dataset object and set in manager
            dataset = Dataset(result["dataframe"], file_path)
            self.dataset_manager.set_dataset(dataset)
            
            # Store in database if available
            try:
                if hasattr(self.db_manager, 'insert_dataset'):
                    with open(file_path, "rb") as f:
                        filebytes = f.read()
                    
                    filename = file_path.split("/")[-1].split("\\")[-1]
                    self.dataset_id = self.db_manager.insert_dataset(filename, filebytes, "import")
                    
                    # Log the import
                    self.logging_service.log_operation(self.dataset_id, "import", f"Imported dataset: {filename}")
            except Exception:
                # Silent fail for database operations
                pass
            
            messagebox.showinfo(
                "Upload Successful", 
                f"Dataset uploaded successfully!\nRows: {len(dataset.data)}"
            )
            
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to load file:\n{str(e)}")
    
    def export_dataset(self):
        """Export dataset"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            messagebox.showwarning("Export", "No dataset loaded to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if not file_path:
            return
        
        try:
            result = self.export_controller.export_dataset(df, file_path, self.dataset_id)
            
            if result["success"]:
                messagebox.showinfo("Export Successful", result["message"])
            else:
                messagebox.showerror("Export Error", result["message"])
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export dataset: {str(e)}")
    
    def show_logs(self):
        """Open the Logs window"""
        if not self.dataset_id:
            messagebox.showwarning("Logs", "No dataset uploaded. Import a dataset first.")
            return
        self.show_frame(LogsWindow)

    def on_closing(self):
        """Properly close connections on app exit"""
        if hasattr(self.db_manager, 'disconnect'):
            self.db_manager.disconnect()
        self.destroy()


class MainMenu(tk.Frame):
    """
    Simple Main Menu matching main_window.py style
    """
    
    def __init__(self, master):
        super().__init__(master, bg=master.light_bg)
        self.master = master
        
        # Simple header
        tk.Label(
            self, 
            text="Main Menu", 
            font=("Arial", 20), 
            bg=master.light_bg
        ).pack(pady=20)

        # Simple buttons in vertical layout
        button_configs = [
            ("Upload Dataset", master.upload_dataset),
            ("Preview Dataset", lambda: master.show_frame(PreviewWindow)),
            ("Data Cleaning", lambda: master.show_frame(CleaningWindow)),
            ("Statistics", lambda: master.show_frame(StatsWindow)),
            ("Visualize", lambda: master.show_frame(VisualizeWindow)),
            ("Feature Engineering", lambda: master.show_frame(FeatureWindow)),
            ("View Logs", lambda: master.show_frame(LogsWindow)),
            ("Export Dataset", master.export_dataset),
        ]

        for text, command in button_configs:
            tk.Button(
                self, 
                text=text, 
                command=command,
                font=("Arial", 10),
                bg=master.accent_color,
                fg='white',
                width=20,
                pady=5
            ).pack(pady=5)


if __name__ == "__main__":
    app = DatasetCleanerUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
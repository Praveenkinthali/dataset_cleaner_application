# data_layer/FileHandler.py

import pandas as pd

class FileHandler:
    """
    Data Layer - Handles file I/O operations
    Supports CSV and Excel formats
    """
    
    def __init__(self):
        self.supported_formats = {
            'csv': ['.csv'],
            'excel': ['.xlsx', '.xls']
        }
    
    def load_file(self, file_path):
        """Load file and return dataframe"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return {"success": False, "message": "Unsupported file format"}
            
            return {"success": True, "dataframe": df, "file_path": file_path}
            
        except Exception as e:
            return {"success": False, "message": f"Error loading file: {str(e)}"}
    
    def save_file(self, dataframe, file_path):
        """Save dataframe to file"""
        try:
            if file_path.endswith('.csv'):
                dataframe.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                dataframe.to_excel(file_path, index=False)
            else:
                return {"success": False, "message": "Unsupported file format"}
            
            return {"success": True, "message": f"File saved to {file_path}"}
            
        except Exception as e:
            return {"success": False, "message": f"Error saving file: {str(e)}"}
    
    def get_supported_export_formats(self):
        """Return list of supported export formats"""
        return [
            ("CSV file", "*.csv"),
            ("Excel file", "*.xlsx")
        ]
    
    def validate_file_path(self, file_path):
        """Validate if file path has supported extension"""
        supported_extensions = [ext for exts in self.supported_formats.values() for ext in exts]
        return any(file_path.endswith(ext) for ext in supported_extensions)
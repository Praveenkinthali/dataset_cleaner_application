# models.py
"""
Core data models for the Dataset Cleaner Application
"""

import pandas as pd
import numpy as np
from datetime import datetime


class Dataset:
    """
    Core Dataset Model
    Represents a dataset with its data and metadata
    """
    
    def __init__(self, data, file_path=None):
        """
        Initialize Dataset
        
        Args:
            data: pandas DataFrame
            file_path: Optional file path string
        """
        self.data = data
        self.file_path = file_path
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
    
    @classmethod
    def load(cls, file_path):
        """
        Load dataset from file
        
        Args:
            file_path: Path to CSV or Excel file
            
        Returns:
            Dataset instance
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format. Use .csv, .xlsx, or .xls")
            
            return cls(df, file_path)
        except Exception as e:
            raise ValueError(f"Error loading file: {str(e)}")
    
    def save(self, file_path):
        """
        Save dataset to file
        
        Args:
            file_path: Destination file path
        """
        try:
            if file_path.endswith('.csv'):
                self.data.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                self.data.to_excel(file_path, index=False)
            else:
                raise ValueError("Unsupported file format. Use .csv or .xlsx")
            
            self.file_path = file_path
            self.modified_at = datetime.now()
        except Exception as e:
            raise ValueError(f"Error saving file: {str(e)}")
    
    def getPreview(self, n_rows=10):
        """Get preview of first n rows"""
        return self.data.head(n_rows)
    
    def getSummaryStatistics(self):
        """Get summary statistics"""
        return self.data.describe()
    
    def getInfo(self):
        """Get dataset info"""
        if self.data is None or self.data.empty:
            return {
                "shape": (0, 0),
                "columns": [],
                "dtypes": {},
                "missing_values": {},
                "memory_usage": 0,
                "created_at": self.created_at,
                "modified_at": self.modified_at
            }
        
        return {
            "shape": self.data.shape,
            "columns": list(self.data.columns),
            "dtypes": self.data.dtypes.to_dict(),
            "missing_values": self.data.isnull().sum().to_dict(),
            "memory_usage": self.data.memory_usage(deep=True).sum() / 1024**2,  # MB
            "created_at": self.created_at,
            "modified_at": self.modified_at
        }
    
    def __repr__(self):
        return f"Dataset(shape={self.data.shape if self.data is not None else 'None'}, file={self.file_path})"
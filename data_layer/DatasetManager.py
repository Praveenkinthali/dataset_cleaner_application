# data_layer/DatasetManager.py

import pandas as pd
import sys
import os

# Add root directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Dataset

class DatasetManager:
    """
    Data Layer - Manages dataset operations
    Handles dataset loading, saving, and manipulation
    """
    
    def __init__(self):
        self.current_dataset = None
        self.dataset_history = []
    
    def load_dataset(self, file_path):
        """Load dataset from file"""
        try:
            self.current_dataset = Dataset.load(file_path)
            return {"success": True, "dataset": self.current_dataset}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_dataset(self):
        """Get current dataset object"""
        return self.current_dataset
    
    def get_dataframe(self):
        """Get current dataframe"""
        if self.current_dataset and hasattr(self.current_dataset, 'data'):
            return self.current_dataset.data
        return pd.DataFrame()  # Return empty DataFrame instead of None
    
    def update_dataframe(self, dataframe):
        """Update current dataset with new dataframe"""
        if self.current_dataset:
            self.current_dataset.data = dataframe
            return {"success": True}
        return {"success": False, "message": "No dataset loaded"}
    
    def set_dataset(self, dataset):
        """Set current dataset"""
        self.current_dataset = dataset
        return {"success": True}
    
    def get_preview(self, n_rows=10):
        """Get preview of dataset"""
        if self.current_dataset:
            return self.current_dataset.getPreview(n_rows)
        return None
    
    def get_statistics(self):
        """Get statistical summary"""
        if self.current_dataset:
            return self.current_dataset.getSummaryStatistics()
        return None
    
    def save_to_history(self):
        """Save current state to history"""
        if self.current_dataset:
            self.dataset_history.append(self.current_dataset.data.copy(deep=True))
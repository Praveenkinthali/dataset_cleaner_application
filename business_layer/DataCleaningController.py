# business_layer/DataCleaningController.py

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class DataCleaningController:
    """
    Business Logic Controller for Data Cleaning Operations
    Orchestrates cleaning operations between UI and Data Layer
    """
    
    def __init__(self, dataset_manager, logging_service):
        """
        Initialize with dependencies
        
        Args:
            dataset_manager: DatasetManager instance
            logging_service: LoggingService instance
        """
        self.dataset_manager = dataset_manager
        self.logging_service = logging_service
    
    def auto_clean(self, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform automatic data cleaning with intelligent defaults
        
        Args:
            dataset_id: Optional dataset ID for logging
            
        Returns:
            Dictionary with cleaning results
        """
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {
                "success": False,
                "message": "No dataset loaded or dataset is empty"
            }
        
        try:
            original_shape = df.shape
            df_cleaned = df.copy()
            
            # Step 1: Replace missing value indicators
            missing_indicators = ['?', '??', '???', 'na', 'NaN', 'NULL', 'null', '--', '', ' ', 'none', 'None']
            df_cleaned = df_cleaned.replace(missing_indicators, np.nan)
            
            # Step 2: Remove completely empty columns
            df_cleaned = df_cleaned.dropna(axis=1, how="all")
            
            # Step 3: Remove columns with >80% missing values
            threshold = 0.8 * len(df_cleaned)
            df_cleaned = df_cleaned.dropna(axis=1, thresh=threshold)
            
            # Step 4: Fill missing values intelligently
            for col in df_cleaned.columns:
                if df_cleaned[col].isnull().any():
                    if df_cleaned[col].dtype.kind in "biufc":  # Numeric
                        if not df_cleaned[col].isna().all():
                            df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
                        else:
                            df_cleaned[col] = df_cleaned[col].fillna(0)
                    else:  # Categorical
                        mode_values = df_cleaned[col].mode()
                        if not mode_values.empty:
                            df_cleaned[col] = df_cleaned[col].fillna(mode_values[0])
                        else:
                            df_cleaned[col] = df_cleaned[col].fillna('Unknown')
            
            # Step 5: Remove duplicate rows
            duplicates_removed = df_cleaned.duplicated().sum()
            df_cleaned = df_cleaned.drop_duplicates()
            
            # Update dataset
            self.dataset_manager.update_dataframe(df_cleaned)
            
            new_shape = df_cleaned.shape
            
            # Log operation
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "cleaning",
                    f"Auto clean: duplicates={duplicates_removed}, columns removed={original_shape[1] - new_shape[1]}"
                )
            
            return {
                "success": True,
                "message": "Dataset cleaned successfully",
                "original_shape": original_shape,
                "new_shape": new_shape,
                "duplicates_removed": duplicates_removed,
                "columns_removed": original_shape[1] - new_shape[1]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Auto cleaning failed: {str(e)}"
            }
    
    def fill_missing_with_mean(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Fill missing values with mean"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        if df[column].dtype.kind not in "biufc":
            return {"success": False, "message": "Mean can only be applied to numeric columns"}
        
        try:
            mean_value = df[column].mean()
            df[column] = df[column].fillna(mean_value)
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "cleaning",
                    f"Filled missing values in '{column}' with mean: {mean_value:.4f}"
                )
            
            return {
                "success": True,
                "message": f"Filled missing values with mean",
                "mean_value": mean_value
            }
        except Exception as e:
            return {"success": False, "message": f"Fill operation failed: {str(e)}"}
    
    def fill_missing_with_mode(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Fill missing values with mode"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        try:
            mode_values = df[column].mode()
            if not mode_values.empty:
                mode_value = mode_values[0]
                df[column] = df[column].fillna(mode_value)
            else:
                mode_value = 'Unknown'
                df[column] = df[column].fillna('Unknown')
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "cleaning",
                    f"Filled missing values in '{column}' with mode: {mode_value}"
                )
            
            return {
                "success": True,
                "message": f"Filled missing values with mode",
                "mode_value": mode_value
            }
        except Exception as e:
            return {"success": False, "message": f"Fill operation failed: {str(e)}"}
    
    def fill_missing_with_custom(self, column: str, value: Any, 
                                dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Fill missing values with custom value"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        try:
            # Try to convert to appropriate type
            if df[column].dtype.kind in "biufc":
                value = float(value) if '.' in str(value) else int(value)
            
            df[column] = df[column].fillna(value)
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "cleaning",
                    f"Filled missing values in '{column}' with custom value: {value}"
                )
            
            return {
                "success": True,
                "message": f"Filled missing values with custom value",
                "custom_value": value
            }
        except Exception as e:
            return {"success": False, "message": f"Fill operation failed: {str(e)}"}
    
    def drop_column(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Drop a column from the dataset"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        try:
            df = df.drop(columns=[column])
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "cleaning",
                    f"Dropped column: {column}"
                )
            
            return {
                "success": True,
                "message": f"Successfully dropped column '{column}'"
            }
        except Exception as e:
            return {"success": False, "message": f"Drop operation failed: {str(e)}"}
    
    def remove_duplicates(self, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Remove duplicate rows"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        try:
            duplicates_count = df.duplicated().sum()
            df = df.drop_duplicates()
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "cleaning",
                    f"Removed {duplicates_count} duplicate rows"
                )
            
            return {
                "success": True,
                "message": f"Removed {duplicates_count} duplicate rows",
                "duplicates_removed": duplicates_count
            }
        except Exception as e:
            return {"success": False, "message": f"Remove duplicates failed: {str(e)}"}
    
    def get_data_quality_summary(self) -> Optional[Dict[str, Any]]:
        """Get data quality summary for UI display"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return None
        
        return {
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "missing_total": df.isnull().sum().sum(),
            "missing_pct": (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100) if df.shape[0] * df.shape[1] > 0 else 0,
            "duplicate_count": df.duplicated().sum(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2
        }
# business_layer/ExportController.py

import pandas as pd
from typing import Dict, Any, Optional


class ExportController:
    """
    Business Logic Controller for Export Operations
    Handles dataset export with logging
    """
    
    def __init__(self, file_handler, db_manager, logging_service):
        """
        Initialize with dependencies
        
        Args:
            file_handler: FileHandler instance for file I/O
            db_manager: DatabaseManager instance for database operations
            logging_service: LoggingService instance for logging
        """
        self.file_handler = file_handler
        self.db_manager = db_manager
        self.logging_service = logging_service
    
    def get_export_formats(self):
        """
        Get list of supported export formats
        
        Returns:
            List of tuples (description, extension)
        """
        return self.file_handler.get_supported_export_formats()
    
    def export_dataset(self, dataframe: pd.DataFrame, file_path: str, 
                      dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Export dataset to file
        
        Args:
            dataframe: DataFrame to export
            file_path: Destination file path
            dataset_id: Optional dataset ID for logging
            
        Returns:
            Dictionary with success status and message
        """
        if dataframe is None or dataframe.empty:
            return {
                "success": False,
                "message": "Cannot export empty dataset"
            }
        
        try:
            # Use FileHandler to save file
            result = self.file_handler.save_file(dataframe, file_path)
            
            if not result["success"]:
                return result
            
            # Extract filename from path
            filename = file_path.split("/")[-1].split("\\")[-1]
            
            # Store export in database if available
            try:
                if (self.db_manager and 
                    hasattr(self.db_manager, 'insert_dataset') and 
                    callable(getattr(self.db_manager, 'insert_dataset', None))):
                    
                    with open(file_path, "rb") as f:
                        filebytes = f.read()
                    
                    export_id = self.db_manager.insert_dataset(filename, filebytes, "export")
                    
                    # Log the export operation
                    self.logging_service.log_operation(
                        dataset_id if dataset_id else export_id,
                        "export",
                        f"Exported dataset to {filename}"
                    )
            except Exception as db_error:
                # File was saved successfully, but database logging failed
                # This is not critical, so we continue
                pass
            
            return {
                "success": True,
                "message": f"Dataset successfully exported to:\n{file_path}\n\nRows: {len(dataframe):,}\nColumns: {len(dataframe.columns):,}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Export failed: {str(e)}"
            }
    
    def export_subset(self, dataframe: pd.DataFrame, file_path: str, 
                     row_indices: Optional[list] = None,
                     columns: Optional[list] = None,
                     dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Export a subset of the dataset
        
        Args:
            dataframe: Source DataFrame
            file_path: Destination file path
            row_indices: Optional list of row indices to export
            columns: Optional list of column names to export
            dataset_id: Optional dataset ID for logging
            
        Returns:
            Dictionary with success status and message
        """
        if dataframe is None or dataframe.empty:
            return {
                "success": False,
                "message": "Cannot export from empty dataset"
            }
        
        try:
            # Create subset
            subset_df = dataframe.copy()
            
            if columns:
                subset_df = subset_df[columns]
            
            if row_indices:
                subset_df = subset_df.iloc[row_indices]
            
            # Export the subset
            return self.export_dataset(subset_df, file_path, dataset_id)
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Subset export failed: {str(e)}"
            }
    
    def quick_export_csv(self, dataframe: pd.DataFrame, file_path: str,
                        dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Quick CSV export with default settings
        
        Args:
            dataframe: DataFrame to export
            file_path: Destination file path (will ensure .csv extension)
            dataset_id: Optional dataset ID for logging
            
        Returns:
            Dictionary with success status and message
        """
        # Ensure .csv extension
        if not file_path.endswith('.csv'):
            file_path += '.csv'
        
        return self.export_dataset(dataframe, file_path, dataset_id)
    
    def quick_export_excel(self, dataframe: pd.DataFrame, file_path: str,
                          dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Quick Excel export with default settings
        
        Args:
            dataframe: DataFrame to export
            file_path: Destination file path (will ensure .xlsx extension)
            dataset_id: Optional dataset ID for logging
            
        Returns:
            Dictionary with success status and message
        """
        # Ensure .xlsx extension
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'
        
        return self.export_dataset(dataframe, file_path, dataset_id)
    
    def validate_export_path(self, file_path: str) -> Dict[str, Any]:
        """
        Validate export file path
        
        Args:
            file_path: File path to validate
            
        Returns:
            Dictionary with validation result
        """
        if not file_path:
            return {
                "valid": False,
                "message": "File path cannot be empty"
            }
        
        if not self.file_handler.validate_file_path(file_path):
            return {
                "valid": False,
                "message": "Unsupported file format"
            }
        
        return {
            "valid": True,
            "message": "Valid export path"
        }
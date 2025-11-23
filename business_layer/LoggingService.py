# business_layer/LoggingService.py

from datetime import datetime
from typing import Dict, Any, List, Optional


class LoggingService:
    """
    Business Logic Service for Logging Operations
    Manages application logging to database and local storage
    """
    
    def __init__(self, db_manager):
        """
        Initialize with database manager
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.local_logs = []  # In-memory log storage for current session
    
    def log_operation(self, dataset_id: int, operation_type: str, 
                     description: str) -> Dict[str, Any]:
        """
        Log an operation to database and local storage
        
        Args:
            dataset_id: Dataset ID
            operation_type: Type of operation (import, export, cleaning, feature_engineering, etc.)
            description: Description of the operation
            
        Returns:
            Dictionary with success status
        """
        try:
            # Log to database if available and has the method
            if (self.db_manager and 
                hasattr(self.db_manager, 'insert_log') and 
                callable(getattr(self.db_manager, 'insert_log', None))):
                self.db_manager.insert_log(dataset_id, operation_type, description)
            
            # Log to local storage
            log_entry = {
                "dataset_id": dataset_id,
                "operation_type": operation_type,
                "description": description,
                "timestamp": datetime.now()
            }
            self.local_logs.append(log_entry)
            
            return {
                "success": True,
                "message": "Operation logged successfully"
            }
        except Exception as e:
            # Fallback: log locally only
            log_entry = {
                "dataset_id": dataset_id,
                "operation_type": operation_type,
                "description": description,
                "timestamp": datetime.now()
            }
            self.local_logs.append(log_entry)
            return {
                "success": True,
                "message": f"Logged locally (database error: {str(e)})"
            }
    
    def log_cleaning_operation(self, dataset_id: int, operation_type: str, 
                               description: str) -> Dict[str, Any]:
        """
        Log a data cleaning operation
        
        Args:
            dataset_id: Dataset ID
            operation_type: Specific cleaning operation type
            description: Description of the cleaning operation
            
        Returns:
            Dictionary with success status
        """
        return self.log_operation(dataset_id, f"cleaning_{operation_type}", description)
    
    def log_feature_operation(self, dataset_id: int, operation_type: str, 
                             description: str) -> Dict[str, Any]:
        """
        Log a feature engineering operation
        
        Args:
            dataset_id: Dataset ID
            operation_type: Specific feature operation type
            description: Description of the feature operation
            
        Returns:
            Dictionary with success status
        """
        return self.log_operation(dataset_id, f"feature_{operation_type}", description)
    
    def get_logs(self, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve logs for a specific dataset or all logs
        
        Args:
            dataset_id: Optional dataset ID to filter logs
            
        Returns:
            Dictionary with logs and success status
        """
        try:
            logs = []
            
            # Get logs from database if available
            if (self.db_manager and 
                hasattr(self.db_manager, 'fetch_logs') and 
                callable(getattr(self.db_manager, 'fetch_logs', None)) and
                dataset_id):
                
                db_logs = self.db_manager.fetch_logs(dataset_id)
                for operation_type, description, timestamp in db_logs:
                    logs.append({
                        "operation_type": operation_type,
                        "description": description,
                        "timestamp": timestamp
                    })
            
            # Add local logs
            if dataset_id:
                local_filtered = [
                    log for log in self.local_logs 
                    if log["dataset_id"] == dataset_id
                ]
                logs.extend(local_filtered)
            else:
                logs.extend(self.local_logs)
            
            # Combine and sort by timestamp
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return {
                "success": True,
                "logs": logs,
                "count": len(logs)
            }
        except Exception as e:
            # Return only local logs if database fails
            if dataset_id:
                local_filtered = [
                    log for log in self.local_logs 
                    if log["dataset_id"] == dataset_id
                ]
                return {
                    "success": True,
                    "logs": sorted(local_filtered, key=lambda x: x["timestamp"], reverse=True),
                    "count": len(local_filtered),
                    "message": f"Using local logs only: {str(e)}"
                }
            else:
                return {
                    "success": True,
                    "logs": sorted(self.local_logs, key=lambda x: x["timestamp"], reverse=True),
                    "count": len(self.local_logs),
                    "message": f"Using local logs only: {str(e)}"
                }
    
    def get_logs_by_operation_type(self, operation_type: str, 
                                   dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve logs filtered by operation type
        
        Args:
            operation_type: Type of operation to filter by
            dataset_id: Optional dataset ID to further filter
            
        Returns:
            Dictionary with filtered logs
        """
        try:
            result = self.get_logs(dataset_id)
            
            if not result["success"]:
                return result
            
            filtered_logs = [
                log for log in result["logs"]
                if log["operation_type"] == operation_type or 
                   log["operation_type"].startswith(operation_type)
            ]
            
            return {
                "success": True,
                "logs": filtered_logs,
                "count": len(filtered_logs)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to filter logs: {str(e)}",
                "logs": []
            }
    
    def get_recent_logs(self, limit: int = 10, 
                       dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get most recent logs
        
        Args:
            limit: Maximum number of logs to return
            dataset_id: Optional dataset ID to filter
            
        Returns:
            Dictionary with recent logs
        """
        try:
            result = self.get_logs(dataset_id)
            
            if not result["success"]:
                return result
            
            recent_logs = result["logs"][:limit]
            
            return {
                "success": True,
                "logs": recent_logs,
                "count": len(recent_logs)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve recent logs: {str(e)}",
                "logs": []
            }
    
    def export_logs(self, file_path: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Export logs to a text file
        
        Args:
            file_path: Destination file path
            dataset_id: Optional dataset ID to filter logs
            
        Returns:
            Dictionary with success status
        """
        try:
            result = self.get_logs(dataset_id)
            
            if not result["success"]:
                return result
            
            logs = result["logs"]
            
            if not logs:
                return {
                    "success": False,
                    "message": "No logs to export"
                }
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("DATASET CLEANER - TRANSFORMATION LOGS\n")
                f.write("=" * 80 + "\n\n")
                
                if dataset_id:
                    f.write(f"Dataset ID: {dataset_id}\n")
                    f.write(f"Total Logs: {len(logs)}\n\n")
                else:
                    f.write(f"All Logs - Total: {len(logs)}\n\n")
                
                f.write("=" * 80 + "\n\n")
                
                for i, log in enumerate(logs, 1):
                    f.write(f"Log Entry #{i}\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Timestamp: {log['timestamp']}\n")
                    f.write(f"Operation: {log['operation_type']}\n")
                    f.write(f"Description: {log['description']}\n")
                    f.write("\n")
            
            return {
                "success": True,
                "message": f"Successfully exported {len(logs)} logs to:\n{file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to export logs: {str(e)}"
            }
    
    def clear_local_logs(self) -> Dict[str, Any]:
        """
        Clear local in-memory logs
        
        Returns:
            Dictionary with success status
        """
        try:
            log_count = len(self.local_logs)
            self.local_logs.clear()
            
            return {
                "success": True,
                "message": f"Cleared {log_count} local logs"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to clear logs: {str(e)}"
            }
    
    def get_log_statistics(self, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get statistics about logs
        
        Args:
            dataset_id: Optional dataset ID to filter
            
        Returns:
            Dictionary with log statistics
        """
        try:
            result = self.get_logs(dataset_id)
            
            if not result["success"]:
                return result
            
            logs = result["logs"]
            
            if not logs:
                return {
                    "success": True,
                    "statistics": {
                        "total_logs": 0,
                        "operation_types": {},
                        "first_log": None,
                        "last_log": None
                    }
                }
            
            # Count by operation type
            operation_counts = {}
            for log in logs:
                op_type = log["operation_type"]
                operation_counts[op_type] = operation_counts.get(op_type, 0) + 1
            
            # Get first and last logs
            sorted_logs = sorted(logs, key=lambda x: x["timestamp"])
            
            return {
                "success": True,
                "statistics": {
                    "total_logs": len(logs),
                    "operation_types": operation_counts,
                    "first_log": sorted_logs[0]["timestamp"],
                    "last_log": sorted_logs[-1]["timestamp"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get statistics: {str(e)}"
            }
    
    def format_log_for_display(self, log: Dict[str, Any]) -> str:
        """
        Format a single log entry for display
        
        Args:
            log: Log entry dictionary
            
        Returns:
            Formatted string
        """
        return (
            f"🕒 {log['timestamp']}\n"
            f"🧩 Operation: {log['operation_type']}\n"
            f"📝 Description: {log['description']}\n"
            + "-" * 80
        )
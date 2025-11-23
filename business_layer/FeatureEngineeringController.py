# business_layer/FeatureEngineeringController.py

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder
from sklearn.decomposition import PCA
from scipy import stats


class FeatureEngineeringController:
    """
    Business Logic Controller for Feature Engineering Operations
    Orchestrates feature transformations between UI and Data Layer
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
        self.undo_stack = []
        self.redo_stack = []
    
    # ========== SCALING OPERATIONS ==========
    
    def standardize_column(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Apply Z-score standardization"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        if df[column].dtype.kind not in "biufc":
            return {"success": False, "message": f"Column '{column}' must be numeric"}
        
        try:
            self._save_undo_state()
            
            scaler = StandardScaler()
            df[column] = scaler.fit_transform(df[[column]])
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "feature_engineering",
                    f"Standardized column '{column}' (mean={scaler.mean_[0]:.4f}, std={scaler.scale_[0]:.4f})"
                )
            
            return {
                "success": True,
                "message": f"Successfully standardized column '{column}'"
            }
        except Exception as e:
            return {"success": False, "message": f"Standardization failed: {str(e)}"}
    
    def minmax_scale_column(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Apply Min-Max normalization (0-1 scaling)"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        if df[column].dtype.kind not in "biufc":
            return {"success": False, "message": f"Column '{column}' must be numeric"}
        
        try:
            self._save_undo_state()
            
            scaler = MinMaxScaler()
            new_col_name = f"{column}_minmax"
            df[new_col_name] = scaler.fit_transform(df[[column]])
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "feature_engineering",
                    f"MinMax scaled column '{column}' to '{new_col_name}'"
                )
            
            return {
                "success": True,
                "message": f"Successfully normalized column '{column}' as '{new_col_name}'"
            }
        except Exception as e:
            return {"success": False, "message": f"Normalization failed: {str(e)}"}
    
    def robust_scale_column(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Apply Robust scaling (median and IQR)"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        if df[column].dtype.kind not in "biufc":
            return {"success": False, "message": f"Column '{column}' must be numeric"}
        
        try:
            self._save_undo_state()
            
            scaler = RobustScaler()
            new_col_name = f"{column}_robust"
            df[new_col_name] = scaler.fit_transform(df[[column]])
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "feature_engineering",
                    f"Robust scaled column '{column}' to '{new_col_name}'"
                )
            
            return {
                "success": True,
                "message": f"Successfully robust scaled column '{column}' as '{new_col_name}'"
            }
        except Exception as e:
            return {"success": False, "message": f"Robust scaling failed: {str(e)}"}
    
    # ========== TRANSFORMATION OPERATIONS ==========
    
    def log_transform_column(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Apply logarithmic transformation"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        if df[column].dtype.kind not in "biufc":
            return {"success": False, "message": f"Column '{column}' must be numeric"}
        
        try:
            self._save_undo_state()
            
            new_col_name = f"{column}_log"
            min_val = df[column].min()
            
            if min_val <= 0:
                shift = abs(min_val) + 1
                df[new_col_name] = np.log(df[column] + shift)
                msg = f"Log transformed '{column}' to '{new_col_name}' (shifted by {shift})"
            else:
                df[new_col_name] = np.log(df[column])
                msg = f"Log transformed '{column}' to '{new_col_name}'"
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(dataset_id, "feature_engineering", msg)
            
            return {"success": True, "message": msg}
        except Exception as e:
            return {"success": False, "message": f"Log transformation failed: {str(e)}"}
    
    def sqrt_transform_column(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Apply square root transformation"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        if df[column].dtype.kind not in "biufc":
            return {"success": False, "message": f"Column '{column}' must be numeric"}
        
        try:
            self._save_undo_state()
            
            new_col_name = f"{column}_sqrt"
            min_val = df[column].min()
            
            if min_val < 0:
                shift = abs(min_val)
                df[new_col_name] = np.sqrt(df[column] + shift)
                msg = f"Square root transformed '{column}' to '{new_col_name}' (shifted by {shift})"
            else:
                df[new_col_name] = np.sqrt(df[column])
                msg = f"Square root transformed '{column}' to '{new_col_name}'"
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(dataset_id, "feature_engineering", msg)
            
            return {"success": True, "message": msg}
        except Exception as e:
            return {"success": False, "message": f"Square root transformation failed: {str(e)}"}
    
    def bin_column(self, column: str, n_bins: int = 5, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Bin numeric column into discrete categories"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        if df[column].dtype.kind not in "biufc":
            return {"success": False, "message": f"Column '{column}' must be numeric"}
        
        try:
            self._save_undo_state()
            
            new_col_name = f"{column}_binned"
            df[new_col_name] = pd.qcut(df[column], n_bins, duplicates='drop', labels=False)
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "feature_engineering",
                    f"Binned '{column}' into {n_bins} quantiles as '{new_col_name}'"
                )
            
            return {
                "success": True,
                "message": f"Successfully binned column '{column}' into {n_bins} bins as '{new_col_name}'"
            }
        except Exception as e:
            return {"success": False, "message": f"Binning failed: {str(e)}"}
    
    def create_polynomial_features(self, column: str, degree: int = 2, 
                                   dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Create polynomial features"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        if df[column].dtype.kind not in "biufc":
            return {"success": False, "message": f"Column '{column}' must be numeric"}
        
        try:
            self._save_undo_state()
            
            new_columns = []
            for d in range(2, degree + 1):
                col_name = f"{column}_poly{d}"
                df[col_name] = df[column] ** d
                new_columns.append(col_name)
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "feature_engineering",
                    f"Created polynomial features for '{column}' up to degree {degree}"
                )
            
            return {
                "success": True,
                "message": f"Successfully created polynomial features: {', '.join(new_columns)}"
            }
        except Exception as e:
            return {"success": False, "message": f"Polynomial features creation failed: {str(e)}"}
    
    # ========== ENCODING OPERATIONS ==========
    
    def one_hot_encode_column(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """One-hot encode categorical column"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        try:
            self._save_undo_state()
            
            dummies = pd.get_dummies(df[column], prefix=column)
            df = pd.concat([df, dummies], axis=1)
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "feature_engineering",
                    f"One-hot encoded column '{column}' into {len(dummies.columns)} columns"
                )
            
            return {
                "success": True,
                "message": f"Successfully one-hot encoded column '{column}' into {len(dummies.columns)} columns"
            }
        except Exception as e:
            return {"success": False, "message": f"One-hot encoding failed: {str(e)}"}
    
    def label_encode_column(self, column: str, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Label encode categorical column"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if column not in df.columns:
            return {"success": False, "message": f"Column '{column}' not found"}
        
        try:
            self._save_undo_state()
            
            le = LabelEncoder()
            new_col_name = f"{column}_label"
            df[new_col_name] = le.fit_transform(df[column].astype(str))
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "feature_engineering",
                    f"Label encoded column '{column}' as '{new_col_name}'"
                )
            
            return {
                "success": True,
                "message": f"Successfully label encoded column '{column}' as '{new_col_name}'"
            }
        except Exception as e:
            return {"success": False, "message": f"Label encoding failed: {str(e)}"}
    
    # ========== ADVANCED OPERATIONS ==========
    
    def apply_pca(self, n_components: int = 2, dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Apply PCA dimensionality reduction"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        
        if len(numeric_cols) < 2:
            return {"success": False, "message": "Need at least 2 numeric columns for PCA"}
        
        if n_components > len(numeric_cols):
            return {"success": False, "message": f"n_components must be <= {len(numeric_cols)}"}
        
        try:
            self._save_undo_state()
            
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(df[numeric_cols])
            
            for i in range(n_components):
                df[f"PC_{i+1}"] = pca_result[:, i]
            
            self.dataset_manager.update_dataframe(df)
            
            variance_explained = sum(pca.explained_variance_ratio_) * 100
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "feature_engineering",
                    f"Applied PCA: {n_components} components from {len(numeric_cols)} features "
                    f"(variance explained: {variance_explained:.1f}%)"
                )
            
            return {
                "success": True,
                "message": f"Successfully applied PCA with {n_components} components "
                          f"(variance explained: {variance_explained:.1f}%)"
            }
        except Exception as e:
            return {"success": False, "message": f"PCA failed: {str(e)}"}
    
    def create_custom_feature(self, feature_name: str, expression: str, 
                             dataset_id: Optional[int] = None) -> Dict[str, Any]:
        """Create custom feature using expression"""
        df = self.dataset_manager.get_dataframe()
        
        if df is None or df.empty:
            return {"success": False, "message": "No dataset loaded"}
        
        if not feature_name or not expression:
            return {"success": False, "message": "Feature name and expression required"}
        
        try:
            self._save_undo_state()
            
            # Safe evaluation with limited namespace
            local_namespace = {
                'df': df,
                'np': np,
                'pd': pd
            }
            
            result = eval(expression, {"__builtins__": {}}, local_namespace)
            df[feature_name] = result
            
            self.dataset_manager.update_dataframe(df)
            
            if dataset_id:
                self.logging_service.log_operation(
                    dataset_id, "feature_engineering",
                    f"Created custom feature '{feature_name}': {expression}"
                )
            
            return {
                "success": True,
                "message": f"Successfully created custom feature '{feature_name}'"
            }
        except Exception as e:
            return {"success": False, "message": f"Custom feature creation failed: {str(e)}"}
    
    # ========== UNDO/REDO OPERATIONS ==========
    
    def _save_undo_state(self):
        """Save current state for undo"""
        df = self.dataset_manager.get_dataframe()
        if df is not None and not df.empty:
            self.undo_stack.append(df.copy(deep=True))
            self.redo_stack.clear()
    
    def undo(self) -> Dict[str, Any]:
        """Undo last operation"""
        if not self.undo_stack:
            return {"success": False, "message": "Nothing to undo"}
        
        current_df = self.dataset_manager.get_dataframe()
        if current_df is not None and not current_df.empty:
            self.redo_stack.append(current_df.copy(deep=True))
        
        previous_df = self.undo_stack.pop()
        self.dataset_manager.update_dataframe(previous_df)
        
        return {"success": True, "message": "Undo applied successfully"}
    
    def redo(self) -> Dict[str, Any]:
        """Redo last undone operation"""
        if not self.redo_stack:
            return {"success": False, "message": "Nothing to redo"}
        
        current_df = self.dataset_manager.get_dataframe()
        if current_df is not None and not current_df.empty:
            self.undo_stack.append(current_df.copy(deep=True))
        
        next_df = self.redo_stack.pop()
        self.dataset_manager.update_dataframe(next_df)
        
        return {"success": True, "message": "Redo applied successfully"}
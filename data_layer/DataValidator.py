# data_layer/DataValidator.py

import pandas as pd
import numpy as np

class DataValidator:
    """
    Data Layer - Validates data quality and integrity
    Performs validation checks on datasets
    """
    
    def __init__(self):
        self.validation_rules = {}
    
    def validate_dataframe(self, df):
        """Comprehensive dataframe validation"""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        if df.empty:
            validation_results["is_valid"] = False
            validation_results["errors"].append("Dataframe is empty")
            return validation_results
        
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            validation_results["warnings"].append(f"Found {missing_count} missing values")
        
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            validation_results["warnings"].append(f"Found {duplicate_count} duplicate rows")
        
        validation_results["info"]["dtypes"] = df.dtypes.value_counts().to_dict()
        validation_results["info"]["shape"] = df.shape
        validation_results["info"]["memory_usage_mb"] = df.memory_usage(deep=True).sum() / 1024**2
        
        return validation_results
    
    def check_missing_values(self, df):
        """Check for missing values in dataframe"""
        missing_summary = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_summary[col] = {
                    "count": missing_count,
                    "percentage": (missing_count / len(df)) * 100
                }
        return missing_summary
    
    def check_data_types(self, df):
        """Check and return data types of all columns"""
        type_info = {}
        for col in df.columns:
            type_info[col] = {
                "dtype": str(df[col].dtype),
                "is_numeric": pd.api.types.is_numeric_dtype(df[col]),
                "is_categorical": pd.api.types.is_categorical_dtype(df[col]),
                "is_datetime": pd.api.types.is_datetime64_any_dtype(df[col])
            }
        return type_info
    
    def check_duplicates(self, df):
        """Check for duplicate rows"""
        duplicates = df[df.duplicated(keep=False)]
        return {
            "duplicate_count": len(duplicates),
            "duplicate_indices": duplicates.index.tolist()
        }
    
    def check_outliers_iqr(self, series):
        """Check for outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        return {
            "outlier_count": len(outliers),
            "outlier_indices": outliers.index.tolist(),
            "lower_bound": lower_bound,
            "upper_bound": upper_bound
        }
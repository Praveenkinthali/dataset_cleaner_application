# data_layer/OutlierDetector.py

import pandas as pd
import numpy as np
from scipy import stats

class OutlierDetector:
    """
    Data Layer - Detects outliers in numerical data
    Uses various statistical methods
    """
    
    def __init__(self):
        self.methods = ['iqr', 'zscore', 'isolation_forest']
    
    def detect_iqr_outliers(self, series, threshold=1.5):
        """Detect outliers using Interquartile Range method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = (series < lower_bound) | (series > upper_bound)
        return outliers
    
    def detect_zscore_outliers(self, series, threshold=3):
        """Detect outliers using Z-score method"""
        z_scores = np.abs(stats.zscore(series.dropna()))
        outliers = pd.Series(False, index=series.index)
        outliers[series.notna()] = z_scores > threshold
        return outliers
    
    def get_outlier_summary(self, df, column_name, method='iqr'):
        """Get detailed outlier summary for a column"""
        if column_name not in df.columns:
            return {"error": "Column not found"}
        
        series = df[column_name]
        
        if not pd.api.types.is_numeric_dtype(series):
            return {"error": "Column is not numeric"}
        
        if method == 'iqr':
            outliers = self.detect_iqr_outliers(series)
        elif method == 'zscore':
            outliers = self.detect_zscore_outliers(series)
        else:
            return {"error": "Unknown method"}
        
        return {
            "method": method,
            "outlier_count": outliers.sum(),
            "outlier_percentage": (outliers.sum() / len(series)) * 100,
            "outlier_indices": df[outliers].index.tolist(),
            "outlier_values": series[outliers].tolist()
        }
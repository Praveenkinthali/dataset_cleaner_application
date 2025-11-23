# data_layer/DataTransformer.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

class DataTransformer:
    """
    Data Layer - Performs data transformations
    Low-level transformation operations
    """
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
    
    def standardize(self, series):
        """Standardize a series (Z-score normalization)"""
        scaler = StandardScaler()
        return pd.Series(scaler.fit_transform(series.values.reshape(-1, 1)).flatten(), 
                        index=series.index)
    
    def normalize(self, series):
        """Normalize series to 0-1 range"""
        scaler = MinMaxScaler()
        return pd.Series(scaler.fit_transform(series.values.reshape(-1, 1)).flatten(),
                        index=series.index)
    
    def log_transform(self, series):
        """Apply logarithmic transformation"""
        min_val = series.min()
        if min_val <= 0:
            shift = abs(min_val) + 1
            return np.log(series + shift)
        return np.log(series)
    
    def sqrt_transform(self, series):
        """Apply square root transformation"""
        min_val = series.min()
        if min_val < 0:
            shift = abs(min_val)
            return np.sqrt(series + shift)
        return np.sqrt(series)
    
    def label_encode(self, series):
        """Label encode categorical series"""
        encoder = LabelEncoder()
        return pd.Series(encoder.fit_transform(series.astype(str)), 
                        index=series.index)
    
    def one_hot_encode(self, series, prefix=None):
        """One-hot encode categorical series"""
        if prefix is None:
            prefix = series.name
        return pd.get_dummies(series, prefix=prefix)
    
    def bin_data(self, series, bins):
        """Bin continuous data into discrete bins"""
        return pd.cut(series, bins=bins, labels=False)
    
    def handle_missing_numeric(self, series, method='mean'):
        """Handle missing values in numeric series"""
        if method == 'mean':
            return series.fillna(series.mean())
        elif method == 'median':
            return series.fillna(series.median())
        elif method == 'mode':
            return series.fillna(series.mode()[0] if not series.mode().empty else 0)
        else:
            return series
    
    def handle_missing_categorical(self, series, method='mode'):
        """Handle missing values in categorical series"""
        if method == 'mode':
            mode_val = series.mode()
            fill_value = mode_val[0] if not mode_val.empty else 'Unknown'
            return series.fillna(fill_value)
        elif method == 'constant':
            return series.fillna('Unknown')
        else:
            return series
import unittest
import pandas as pd
import numpy as np
from data_layer.DataValidator import DataValidator

class TestDataValidator(unittest.TestCase):
    """Unit tests for DataValidator class"""

    def setUp(self):
        """Setup sample dataframe for testing"""
        self.validator = DataValidator()
        self.df = pd.DataFrame({
            "Name": ["Raju", "Ajay", "Ravi", "Raju"],
            "Age": [25, np.nan, 30, 25],
            "Score": [88.5, 92.0, np.nan, 88.5],
            "JoinDate": pd.to_datetime(["2020-01-01", "2021-06-10", "2022-09-15", "2020-01-01"])
        })

    def test_validate_dataframe_valid(self):
        """Test comprehensive dataframe validation"""
        result = self.validator.validate_dataframe(self.df)
        self.assertIn("is_valid", result)
        self.assertTrue(result["is_valid"])
        self.assertIn("warnings", result)
        self.assertGreaterEqual(len(result["info"]), 3)

    def test_validate_dataframe_empty(self):
        """Test validation on empty dataframe"""
        empty_df = pd.DataFrame()
        result = self.validator.validate_dataframe(empty_df)
        self.assertFalse(result["is_valid"])
        self.assertIn("Dataframe is empty", result["errors"])

    def test_check_missing_values(self):
        """Check detection of missing values"""
        missing = self.validator.check_missing_values(self.df)
        self.assertIn("Age", missing)
        self.assertIn("Score", missing)
        self.assertTrue(missing["Age"]["count"] > 0)
        self.assertTrue(0 < missing["Age"]["percentage"] <= 100)

    def test_check_missing_values_no_missing(self):
        """Check behavior when no missing values exist"""
        df_no_missing = self.df.fillna(0)
        missing = self.validator.check_missing_values(df_no_missing)
        self.assertEqual(missing, {})

    # --------------------- check_data_types() ---------------------
    def test_check_data_types(self):
        """Verify that data types are correctly identified"""
        types = self.validator.check_data_types(self.df)
        self.assertIn("Age", types)
        self.assertTrue(types["Age"]["is_numeric"])
        self.assertTrue(types["JoinDate"]["is_datetime"])
        self.assertFalse(types["Name"]["is_numeric"])

    # --------------------- check_duplicates() ---------------------
    def test_check_duplicates(self):
        """Detect duplicate rows in dataframe"""
        result = self.validator.check_duplicates(self.df)
        self.assertIn("duplicate_count", result)
        self.assertGreaterEqual(result["duplicate_count"], 1)
        self.assertIsInstance(result["duplicate_indices"], list)

    def test_check_duplicates_no_duplicates(self):
        """When no duplicates exist"""
        df_unique = self.df.drop_duplicates()
        result = self.validator.check_duplicates(df_unique)
        self.assertEqual(result["duplicate_count"], 0)
        self.assertEqual(result["duplicate_indices"], [])

    # --------------------- check_outliers_iqr() ---------------------
    def test_check_outliers_iqr(self):
        """Detect outliers in a numeric series using IQR method"""
        series = pd.Series([10, 12, 14, 16, 18, 300])  
        result = self.validator.check_outliers_iqr(series)
        self.assertIn("outlier_count", result)
        self.assertEqual(result["outlier_count"], 1)
        self.assertTrue(all(k in result for k in ["lower_bound", "upper_bound"]))

    def test_check_outliers_iqr_no_outliers(self):
        """Series without any outliers"""
        series = pd.Series([10, 11, 12, 13, 14, 15])
        result = self.validator.check_outliers_iqr(series)
        self.assertEqual(result["outlier_count"], 0)
        self.assertEqual(result["outlier_indices"], [])

if __name__ == '__main__':
    unittest.main()

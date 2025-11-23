# data_layer/DatabaseManager.py
"""
Enhanced DatabaseManager with automatic database and table creation
Replace your existing DatabaseManager.py with this version
"""

import mysql.connector
from mysql.connector import Error
import logging

class DatabaseManager:
    """
    Data Layer - Handles all database operations
    Manages MySQL connections and CRUD operations
    ✨ NEW: Automatically creates database and tables if they don't exist
    """
    
    def __init__(self, host='localhost', user='root', password='', database='dataset_cleaner', port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        logger = logging.getLogger('DatabaseManager')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    def connect(self):
        """
        Establish database connection
        ✨ Automatically creates database and tables if they don't exist
        """
        try:
            # Step 1: Connect WITHOUT specifying database
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            cursor = temp_connection.cursor()
            
            # Step 2: Create database if it doesn't exist
            self.logger.info(f"Checking if database '{self.database}' exists...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.logger.info(f"✅ Database '{self.database}' ready")
            
            cursor.close()
            temp_connection.close()
            
            # Step 3: Connect to the database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True
            )
            
            self.logger.info(f"✅ Connected to MySQL database: {self.database} at {self.host}:{self.port}")
            
            # Step 4: Create tables if they don't exist
            self._create_tables()
            
            return True
            
        except Error as err:
            self.logger.error(f"❌ Error connecting to MySQL: {err}")
            return False
    
    def _create_tables(self):
        """
        Create required tables if they don't exist
        ✨ NEW: Automatic table creation
        """
        try:
            cursor = self.connection.cursor()
            
            # Create dataset table
            dataset_table_query = """
            CREATE TABLE IF NOT EXISTS dataset (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                filedata LONGBLOB NOT NULL,
                operation_type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_timestamp (timestamp),
                INDEX idx_operation (operation_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            
            cursor.execute(dataset_table_query)
            self.logger.info("✅ Table 'dataset' ready")
            
            # Create log table
            log_table_query = """
            CREATE TABLE IF NOT EXISTS log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                dataset_id INT NOT NULL,
                operation_type VARCHAR(100) NOT NULL,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dataset_id) REFERENCES dataset(id) ON DELETE CASCADE,
                INDEX idx_dataset (dataset_id),
                INDEX idx_timestamp (timestamp),
                INDEX idx_operation (operation_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            
            cursor.execute(log_table_query)
            self.logger.info("✅ Table 'log' ready")
            
            cursor.close()
            
            self.logger.info("✅ All database tables initialized successfully")
            
        except Error as err:
            self.logger.error(f"❌ Error creating tables: {err}")
            raise
    
    def verify_connection(self):
        """
        Verify database connection is active
        Returns True if connected, False otherwise
        """
        try:
            if self.connection and self.connection.is_connected():
                return True
            return False
        except:
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("MySQL connection closed.")
            self.connection = None
    
    def insert_dataset(self, filename, filebytes, operation_type):
        """Insert dataset record into database"""
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO dataset (filename, filedata, operation_type) VALUES (%s, %s, %s)"
            cursor.execute(sql, (filename, filebytes, operation_type))
            self.connection.commit()
            dataset_id = cursor.lastrowid
            cursor.close()
            self.logger.info(f"✅ Dataset '{filename}' inserted with ID: {dataset_id}")
            return dataset_id
        except Error as err:
            self.logger.error(f"❌ Error inserting dataset: {err}")
            return None
    
    def insert_log(self, dataset_id, operation_type, description):
        """Insert log entry into database"""
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO log (dataset_id, operation_type, description) VALUES (%s, %s, %s)"
            cursor.execute(sql, (dataset_id, operation_type, description))
            self.connection.commit()
            cursor.close()
            self.logger.info(f"✅ Log entry created for dataset ID: {dataset_id}")
        except Error as err:
            self.logger.error(f"❌ Error inserting log: {err}")
    
    def fetch_datasets(self):
        """Fetch all datasets from database"""
        try:
            cursor = self.connection.cursor()
            sql = "SELECT id, filename, operation_type, timestamp FROM dataset ORDER BY timestamp DESC"
            cursor.execute(sql)
            datasets = cursor.fetchall()
            cursor.close()
            return datasets
        except Error as err:
            self.logger.error(f"❌ Error fetching datasets: {err}")
            return []
    
    def fetch_logs(self, dataset_id):
        """Fetch logs for specific dataset"""
        try:
            cursor = self.connection.cursor()
            sql = "SELECT operation_type, description, timestamp FROM log WHERE dataset_id = %s ORDER BY timestamp DESC"
            cursor.execute(sql, (dataset_id,))
            logs = cursor.fetchall()
            cursor.close()
            return logs
        except Error as err:
            self.logger.error(f"❌ Error fetching logs: {err}")
            return []
    
    def delete_dataset(self, dataset_id):
        """Delete dataset from database"""
        try:
            cursor = self.connection.cursor()
            sql = "DELETE FROM dataset WHERE id = %s"
            cursor.execute(sql, (dataset_id,))
            self.connection.commit()
            cursor.close()
            self.logger.info(f"✅ Dataset ID {dataset_id} deleted")
        except Error as err:
            self.logger.error(f"❌ Error deleting dataset: {err}")
    
    def test_connection(self):
        """
        Test database connection and table existence
        Returns dict with status information
        """
        result = {
            "connected": False,
            "database_exists": False,
            "tables_exist": False,
            "tables": []
        }
        
        try:
            if not self.connection or not self.connection.is_connected():
                return result
            
            result["connected"] = True
            
            cursor = self.connection.cursor()
            
            # Check database
            cursor.execute("SELECT DATABASE()")
            db = cursor.fetchone()
            if db and db[0] == self.database:
                result["database_exists"] = True
            
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            result["tables"] = tables
            
            if 'dataset' in tables and 'log' in tables:
                result["tables_exist"] = True
            
            cursor.close()
            
        except Error as err:
            self.logger.error(f"Error testing connection: {err}")
        
        return result
    
    def get_database_info(self):
        """
        Get database information for diagnostics
        """
        info = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "database": self.database,
            "connected": self.verify_connection()
        }
        
        if info["connected"]:
            test_result = self.test_connection()
            info.update(test_result)
        
        return info
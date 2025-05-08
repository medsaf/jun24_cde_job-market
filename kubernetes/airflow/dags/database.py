import mysql.connector
import logging
import os
from contextlib import contextmanager
from dotenv import load_dotenv


#load_dotenv(dotenv_path=".env.test") # Load environment variables from .env file

class DatabaseConfig:
    """Database configuration class to store connection parameters."""
    def __init__(self, host=os.getenv("DB_HOST", "sqlclusterip.default.svc.cluster.local"), database=os.getenv("DB_NAME", "francetravail"), user=os.getenv("DB_USER", "root"), password=os.getenv("DB_PASSWORD", "password"), port=os.getenv("DB_PORT", "3306")):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        #self.charset = charset

    def get_connection(self):
        """Create and return a connection based on the config."""
        return mysql.connector.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port
            #charset=self.charset
        )

def get_Elasticsearch():
    """Create and return an Elasticsearch client."""
    from elasticsearch import Elasticsearch
    es_config = {
        "hosts": [{
            "host": os.getenv("ES_HOST", "localhost"),
            "port": int(os.getenv("ES_PORT", 9200)),
            "scheme": "http"  # Use "https" if your cluster is set up to use SSL
        }]
    }
    return Elasticsearch(**es_config)


# Instantiate the DatabaseConfig
db_config = DatabaseConfig()

@contextmanager
def get_db():
    """Context manager for FastAPI to handle db connections and cursors."""
    try:
        connection = db_config.get_connection()  # Get connection from DatabaseConfig
        
        cursor = connection.cursor(dictionary=True, buffered=True)
        yield cursor  # Return the cursor for the API route
    except mysql.connector.Error as e:
        logging.error(f"Database connection error: {e}")
        yield None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_db_persistent():
    """Create a persistent connection for database setup."""
    connection = db_config.get_connection()  # Get connection from DatabaseConfig
    cursor = connection.cursor(dictionary=False, buffered=True)
    return cursor, connection

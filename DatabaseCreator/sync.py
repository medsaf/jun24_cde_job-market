import os
import time
import pandas as pd
from elasticsearch import Elasticsearch
from database import get_db_persistent, get_Elasticsearch
from dotenv import load_dotenv



# Get persistent connection (cursor, connection) for MySQL
cursor, connection = get_db_persistent()

print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")

# Elasticsearch client setup


es = get_Elasticsearch()  # Initialize Elasticsearch client

# Fetch data from MySQL
def fetch_data_from_mysql():
    cursor.execute("SELECT job_id, description FROM job")  # Replace with your actual query
    data = cursor.fetchall()
    return data

# Insert data into Elasticsearch
def insert_into_elasticsearch(data):
    for index, row in enumerate(data):
        doc = {
            'job_id': row[0],  # Map your MySQL columns to Elasticsearch fields
            'description': row[1],
            # Add other fields as necessary
        }
        es.index(index="job_index", id=row[0], document=doc)  # Adjust index name accordingly

def main():
    data = fetch_data_from_mysql()  # Fetch data from MySQL
    insert_into_elasticsearch(data)  # Insert data into Elasticsearch
    print("✅ Data successfully loaded into Elasticsearch!")

if __name__ == "__main__":
    main()

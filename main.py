import requests
import json
import os
import time
import mysql.connector
import pandas as pd
import sys
sys.path.append("C:/Users/medsa/Desktop/projet_DE")
from sql.CreateDataFileModel import *
from FranceTravailAPIExtractor.FranceTravailDataExtractor import *
from pathlib import Path

""" host= "127.0.0.1"
port="56376"
user="root"
password="password"
dbName="mydb"
os.environ["host"]=host
os.environ["port"]=port
os.environ["user"]=user
os.environ["password"]=password
os.environ["DB"]=dbName """
#### Getting environment variable
OUTPUT_DIR = Path().absolute()
ip=os.getenv("host")
port=os.getenv("port")
user=os.getenv("user")
password=os.getenv("passowrd")
dbName=os.getenv("DB")
#### check if model point is created
modelCreated=CheckIfModelIsCreated(ip="localhost",port=port,user="root",password="password",dbName="mydb")
if not modelCreated:
    print("====== Creating Database model ====")
    print(f"1-Creating Queries according to DB model")
    createDBModel(OUTPUT_DIR,csv_file_name="table_columns_modified.csv")
    print(f"2-Creating Database {dbName}")
    DBS=createDB(ip=ip,port=port,user=user,password=password,dbName=dbName)
    print(f"Existing {DBS}")
    print(f"3-Creating tables inside DB")
    TAB=createTableintoDF(ip=ip,port=port,user=user,password=password,dbName=dbName,OUTPUT_DIR=OUTPUT_DIR)
    print(f"created Tables {TAB}")
    print("====== Database model is created ====")

#### Extracting data and inserting it into model point
print("==== Extracting data and inserting it into model point ====")
API_RES=Extract_data(OUTPUT_DIR)
print("===== Inserting data into model =====")
insertDataToDB(API_RES,csv_file_name="table_columns_modified.csv",ip=ip,port=port,user=user,password=password,dbName="mydb",OUTPUT_DIR=OUTPUT_DIR)
print("===== Data insertion is complete =====")

from sqlalchemy import create_engine, MetaData, text, Integer, String
from sqlalchemy.schema import Column, Table
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI
from pydantic import BaseModel
import os
import mariadb
import mlflow
import pandas as pd

"""python3 -m uvicorn main:api --reload"""
api = FastAPI() 

mysql_user = "root"

mysql_password = "password"

mysql_host = "127.0.0.1"

mysql_port = 8000

mysql_database = "francetravail"

model_name = "FranceTravailSalaryExtract"

model_version = "latest"

def getData(job_id,mysql_user=mysql_user,mysql_password =mysql_password,mysql_host=mysql_host,mysql_port = mysql_port,mysql_database =mysql_database):
    try:
         conn = mariadb.connect(
            user=mysql_user,
            password=mysql_password,
            host=mysql_host,
            port=mysql_port,
            database=mysql_database

         )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return(None)
    
    try:
        job_tab=pd.read_sql_query(f"select * from job where job_id={job_id}",conn)
        return(job_tab)
    except mariadb.Error as e:
        print(f"item not found: {e}")
        return (None)
    
# Load the model back for predictions as a generic Python Function model    
def loadModel(model_name = model_name,model_version = model_version):
    model_uri = f"models:/{model_name}/{model_version}"
    model = mlflow.sklearn.load_model(model_uri)
    return model


@api.get("/salary/{job_id}")
async def get_tables(job_id):
    job_tab=getData(job_id)
    d={"job_id":str(job_tab["job_id"][0]),"title":job_tab["title"][0]}
    model=loadModel()
    d={"job_id":str(job_tab["job_id"][0]),"title":job_tab["title"][0]}    
    return(d)
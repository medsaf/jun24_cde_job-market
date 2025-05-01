import os
import mysql.connector
from joblib import load
import pandas as pd

"""python3 -m uvicorn main:api --reload"""

mysql_user = "root"

mysql_password = "password"

#mysql_host = "192.168.49.2"

#mysql_port = 30000 

mysql_host =  "sqlclusterip.default.svc.cluster.local"

mysql_port = "3306"

#mysql_port = 51980

mysql_database = "francetravail"

def getData(job_id,mysql_user=mysql_user,mysql_password =mysql_password,mysql_host=mysql_host,mysql_port = mysql_port,mysql_database =mysql_database):
    try:
         conn = mysql.connector.connect(
            user=mysql_user,
            password=mysql_password,
            host=mysql_host,
            port=mysql_port,
            database=mysql_database
         )
    except mysql.connector.Error as e:
        print(f"Error connecting to MySqLDB Platform: {e}")
        return(None)
    
    try:
        job_tab=pd.read_sql_query(f"select * from job where job_id={job_id}",conn)
        return(job_tab)
    except mysql.connector.Error as e:
        print(f"item not found: {e}")
        return (None)
    
getData(1)

def loadModel(path_to_model=os.getcwd()+"/DatabaseCreator"+"/savedModels/model.pckl"):
    return load(path_to_model)

print(os.getcwd())


def getPrediction(id):
    job=getData(id)
    print(job)
    job.loc[:,"insee_code"]=job["insee_code"]//1000*1000
    model=loadModel(path_to_model="./savedModels/model.pckl")
    return(model.predict(job.loc[:,['rome_code', 'experience_required', 'experience_length_months', 'is_alternance', 'candidates_missing', 'moving_code', 'insee_code']]))
    

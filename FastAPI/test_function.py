import os
import mariadb

"""python3 -m uvicorn main:api --reload"""


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
    

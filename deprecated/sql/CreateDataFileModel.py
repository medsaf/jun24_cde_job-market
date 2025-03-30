import pandas as pd
import mysql.connector
import os
import uuid
from sqlalchemy import create_engine
import pymysql
import re

def get_tables_names(API_RES,OUTPUT_DIR="."):
    """
    function to extract tables names in order to create tables
    """
    tables=["salaire","entreprise","lieuTravail","contact"]
    tabNames={}
    namesDF=pd.DataFrame(columns=("table","filedName"))
    for tabName in tables:
        colnames=[]
        for res in API_RES:
            colnames=colnames+list(res[tabName].keys()) 
        add_cols=set(colnames)
        add_cols.update([tabName+"_id"])
        tabNames[tabName]=add_cols
        namesDF=pd.concat([namesDF,pd.DataFrame([(tabName,name) for name in add_cols],columns=("table","filedName"))])
    ### compétence est une liste de dictionnaire
    interm=[list(d.keys()) for d in res["competences"] for res in API_RES]
    final_compt_names=set([name for li in interm for name in li ])
    final_compt_names.update(["competence_id"])
    tabNames["competence"]=final_compt_names
    namesDF=pd.concat([namesDF,pd.DataFrame([("competence",name) for name in final_compt_names],columns=("table","filedName"))])
    ### Final table 
    job_names=set(res.keys())
    job_names.update([x+"_id" for x in tabNames.keys()])
    job_names.difference_update(tabNames.keys())
    tabNames["job"]=job_names
    namesDF=pd.concat([namesDF,pd.DataFrame([("job",name) for name in job_names],columns=("table","filedName"))])
    namesDF.reindex()
    ### Names to be saved in a csv file
    file_name="table_columns"
    namesDF.to_csv(OUTPUT_DIR+"/sql/"+file_name+".csv")
    return (tabNames)

def createDBModel(OUTPUT_DIR,csv_file_name="table_columns_modified.csv"):
    df=pd.read_csv(OUTPUT_DIR+"/sql/"+csv_file_name)
    prepTabNames=df["table"].unique()
    for tabName in prepTabNames:
        tabString="DROP TABLE IF EXISTS "+tabName+";\n"+"CREATE TABLE IF NOT EXISTS "+tabName+"(\n"
        tabDF=df[df["table"]==tabName]
        ### Create Field
        for i in range(len(tabDF)):
            line=tabDF.iloc[i]
            tabString+=line["filedName"]+" "+line["dataType"]+" "+(line["option"] if pd.notna(line["option"]) else "")+" ,\n"
        ### ADD primary keys
        primaryKey=tabDF[tabDF["primaryKey"]==1]
        if len(primaryKey)>=1:
            delimiter=","
            tabString+="PRIMARY KEY ( "+delimiter.join(primaryKey["filedName"]) +" )\n"
        ### ADD foreign Keys
        foreignKey=tabDF[tabDF["foreignKey"]==1].reset_index()
        if (len(foreignKey)>=1):
            foreignKey.apply(lambda line:"CONSTRAINT "+ line["filedName"]+" REFRENCES "+line["referenceTable"]+"("+line["filedName"]+" )\n",axis=1).to_list()
            delimiter=",\n"
            fkstring=delimiter.join(foreignKey.apply(lambda line:"CONSTRAINT "+ line["filedName"]+" REFRENCES "+line["referenceTable"]+"("+line["filedName"]+" )",axis=1).to_list())
            tabString+=fkstring
        ### close query
        tabString+=");\n"
        with open(OUTPUT_DIR+"/sql/ModelDB/"+tabName+".txt","w+") as file:
            file.write(tabString)
            file.close()

def createDB(ip="localhost",port=3306,user="root",password="password",dbName="mydb"):
    cnx = mysql.connector.MySQLConnection(user=user, password=password,
                host=ip,auth_plugin='mysql_native_password',port=port)
    cursor=cnx.cursor()
    query="CREATE DATABASE "+dbName+";"
    DBS=[]
    try:
        cursor.execute(query)
        cursor.execute("SHOW DATABASES;") 
        res=cursor.fetchall()
        for r in res:
            print(r)
            DBS.append(r)
    except:
        cnx.rollback() 
    cnx.close()  
    return(DBS)

def createTableintoDF(ip="localhost",port=3306,user="root",password="password",dbName="mydb",OUTPUT_DIR="./"):
    cnx = mysql.connector.MySQLConnection(user=user, password=password,database=dbName,
                host=ip,auth_plugin='mysql_native_password',port=port)
    cursor=cnx.cursor()
    files=os.listdir(OUTPUT_DIR+"/sql/ModelDB")
    if len(files)>0:
        files.pop(files.index("job.txt"))
        files.insert(len(files),"job.txt")
        for file in files:
            print(file)
            with open(OUTPUT_DIR+"/sql/ModelDB/"+file,"r") as idFile:
                query=idFile.read()
                idFile.close()
            try:
                cursor.execute(query)
                cnx.commit()
            except:
                cnx.rollback() 
    cnx.close()
    ### Print available Tables
    cnx = mysql.connector.MySQLConnection(user=user, password=password,database=dbName,
                host=ip,auth_plugin='mysql_native_password')
    cursor=cnx.cursor()
    tableNames=[]
    try:
        cursor.execute("show tables;")
        cnx.commit()
        res=cursor.fetchall()
        for r in res:
            tableNames.append(r)
    except:
        cnx.rollback() 
    cnx.close()
    return(tableNames)

def insertDataToDB(API_RES,csv_file_name="table_columns_modified.csv",ip="localhost",port=3306,user="root",password="password",dbName="mydb",OUTPUT_DIR="./"):
   
    tableNames=["salaire","entreprise","competence","lieuTravail","contact"]
    colsDf=pd.read_csv(OUTPUT_DIR+"/sql/"+csv_file_name)
    #tabName="competence"
    #tabName="lieuTravail"
    #tabName="salaire"
    tabName="entreprise"
    engine=create_engine("mysql+pymysql://{user}:{pw}@{host}:{port}/{db}".format(host=ip,port=port, db=dbName, user=user, pw=password))
    idsDF={}
    for tabName in tableNames:
        print(tabName)
        #res=API_RES[1]
        colDF=colsDf[colsDf["table"]==tabName]
        inputDF=pd.DataFrame(columns=colDF["filedName"].unique()) 
        for res in API_RES:
            rowFormat= pd.DataFrame(columns=colDF[colDF["filedName"]!=tabName+"_id"]["filedName"].unique())
            if (res["id"] not in idsDF.keys()):
                idsDF[res["id"]]={}
            if tabName in res.keys():
                record=res[tabName]
                rowFormat=pd.concat([rowFormat,pd.json_normalize(record)])
                rowId=pd.util.hash_pandas_object(rowFormat).loc[0]
                idsDF[res["id"]][tabName+'_id']=str(rowId)
                rowFormat[tabName+"_id"]=str(rowId)
                inputDF=pd.concat([inputDF,rowFormat[inputDF.columns]])
            elif tabName=="competence" and "competences" in res.keys():
                records=res["competences"]
                idsDF[res["id"]][tabName+'_id']=[]
                for record in records:
                    rowFormat= pd.DataFrame(columns=colDF[colDF["filedName"]!=tabName+"_id"]["filedName"].unique())
                    rowFormat=pd.concat([rowFormat,pd.json_normalize(record)])
                    rowId=pd.util.hash_pandas_object(rowFormat).loc[0]
                    idsDF[res["id"]][tabName+'_id']+=[str(rowId)]
                    rowFormat[tabName+"_id"]=str(rowId)
                    inputDF=pd.concat([inputDF,rowFormat])
        inputDF.drop_duplicates(subset=[tabName+"_id"],inplace=True,ignore_index=True)
        dictType=colsDf[colsDf["table"]==tabName].set_index("filedName")["pdType"].to_dict()
        #inputDF.to_html(OUTPUT_DIR+"/entreprise.html")
        inputDF.astype(dictType)
        inputDF.reset_index() 
        inputDF.to_sql(tabName.lower(),engine,index=False,if_exists="append")
    print(f"{tableNames} inserted into DB")   
    #### job table
    ID=[]
    for key in idsDF.keys():
        idsDF[key]["id"]=key
        ID.append(idsDF[key])
    FinalIDDF=pd.json_normalize(ID).explode(column="competence_id")
    tabName="job"
    colDF=colsDf[colsDf["table"]==tabName]
    fieldNames=set(colDF["filedName"].unique()).difference([tab+"_id" for tab in tableNames]).difference(["origineOffre","agence","permis"])
    inputDF=pd.DataFrame(columns=list(fieldNames))
    for res in API_RES:
        record={key:res[key] if key in res.keys() else None for key in fieldNames}
        inputDF=pd.concat([inputDF,pd.json_normalize(record)])
    #### add foreign keys
    inputDF=FinalIDDF.merge(inputDF,on="id")
    ####
    dictType=colsDf[(colsDf["table"]==tabName) & (colsDf["filedName"].isin(fieldNames))].set_index("filedName")["pdType"].to_dict()
    inputDF.astype(dictType)
    inputDF.reset_index()     
    inputDF.to_sql(tabName.lower(),engine,method="multi",index=False,if_exists="append")

def CheckIfModelIsCreated(ip="localhost",port=3306,user="root",password="password",dbName="mydb"):
    cnx = mysql.connector.MySQLConnection(user=user, password=password,
                host=ip,auth_plugin='mysql_native_password',port=port)
    cursor=cnx.cursor()
    cursor.execute("show databases;")
    res=cursor.fetchall()
    return ((dbName,) in res)

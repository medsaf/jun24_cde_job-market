import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from joblib import dump
import mysql.connector





""" user="root"
password="password"
host="127.0.0.1"
port=30000
database="francetravail"
 """


##### 

def load_and_format_data_and_create_model(user=user,password=password,host=host,port=port,database=database):
    try:
        conn = mysql.connector.connect(
            user=user,
            password=password,
            #host="127.0.0.1",
            host=host,
            #port=8000,
            port=port,
            #port=3306,
            #database="francetravail"
            database=database
            )
    except mysql.connector.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cur = conn.cursor()    

    ##### Extract data and prepare input table 

    tab_name="job"
    job_tab=pd.read_sql_query("select * from job",conn)
    #### remove columns with a lot of NA
    job=job_tab.loc[:,job_tab.isna().sum()==0]
    job.loc[:,"insee_code"]=job["insee_code"]//1000*1000
    cols_to_drop=["description","creation_date","update_date","internal_id","title"]
    job=job.loc[:,~job.columns.isin(cols_to_drop)]
    job.head()
    #### Merge salary
    salary=pd.read_sql_query("select * from salary", conn)
    salary.head()
    total_bins=5
    labels=[i for i in range(total_bins)]
    salary["salary_label"] = pd.qcut(salary['min_monthly_salary'], [i/total_bins for i in range(total_bins+1)], labels=labels)
    final_data=job.merge(salary.loc[:,["job_id","salary_label"]],on="job_id")
    ##### Create model 
    columns=list(job.columns)
    columns.remove("job_id")
    print(columns)
    categorical_features = columns
    categorical_transformer = OneHotEncoder(drop = "first", sparse=False)
    pca_properties=PCA(n_components=120)
    #Column Tranformer pour appliquer les transformations sur certaines colonnes
    preprocessor = Pipeline(
        steps=[("preprocessor", categorical_transformer), 
            ("pca", pca_properties)]
    )
    final_preprocessor = ColumnTransformer(
        transformers=[
            ("cat",preprocessor, categorical_features)
        ]
    )

    RF = RandomForestClassifier(max_depth=10, random_state=0)
    estimator= Pipeline(steps=[("preprocess",final_preprocessor),
                            ("RF_estimator",RF)])

    ##### Train model
    target_cols="salary_label"
    feats_cols=columns
    X_train, X_test, y_train, y_test = train_test_split(final_data.loc[:,feats_cols], final_data.loc[:,target_cols], test_size=0.10, random_state = 42)
    estimator.fit(X_train, y_train)  


    ##### Test model
    X_test=X_test[X_test["rome_code"].isin(X_train["rome_code"])]
    y_test=y_test[y_test.index.isin(X_test.index)]
    accuracy=estimator.score(X_test,y_test)

    return estimator


##### Save model 
def save_model(model,path_to_model='dags/repo/kubernetes/airflow/dags/savedModels/model.pckl'):
    # training the model
    # saving model
    print(str(model), 'saved at ', path_to_model)
    dump(model, path_to_model)



def update_model(path_to_model="dags/repo/kubernetes/airflow/dags/savedModels/model_V2.pckl"):
    user="root"
    password="password"
    host="sqlclusterip.default.svc.cluster.local"
    port=3306
    database="francetravail"
    estimator=load_and_format_data_and_create_model(user=user,password=password,host=host,port=port,database=database)
    save_model(estimator,path_to_model=path_to_model)






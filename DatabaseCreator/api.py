from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database import get_db, get_Elasticsearch # Import new database function
from getPredictions import *
from elasticsearch import Elasticsearch
import os

app = FastAPI()


"""python3 -m uvicorn main:api --reload"""

mysql_user = "root"

mysql_password = "password"

mysql_host = "127.0.0.1"

#mysql_host = "192.168.49.2"


mysql_port = 8000

#mysql_port = 51980


mysql_database = "francetravail"


"""python3 -m uvicorn main:api --reload"""

es = get_Elasticsearch()  # Initialize Elasticsearch client

class SearchPayload(BaseModel):
    must_contain: Optional[List[str]] = None
    contain_any: Optional[List[str]] = None
    not_contain: Optional[List[str]] = None
    exact_match: Optional[bool] = False
    

def search_in_elasticsearch(payload: SearchPayload):
    try:
        if payload.exact_match:
            es_query = {
                "query": {
                    "bool": {
                        "must": [{"term": {"description.keyword": word}} for word in (payload.must_contain or [])],
                        "should": [{"term": {"description.keyword": word}} for word in (payload.contain_any or [])],
                        "must_not": [{"term": {"description.keyword": word}} for word in (payload.not_contain or [])]
                    }
                }
            }
        else:
            es_query = {
                "query": {
                    "bool": {
                        "must": [{"match": {"description": {"query": word, "fuzziness": "AUTO"}}} for word in (payload.must_contain or [])],
                        "should": [{"match": {"description": {"query": word, "fuzziness": "AUTO"}}} for word in (payload.contain_any or [])],
                        "must_not": [{"match": {"description": word}} for word in (payload.not_contain or [])]
                    }
                }
            }
        # Send the search query to Elasticsearch
        es_results = es.search(index="job_index", body=es_query)
        
        # Extract matching IDs from Elasticsearch results
        matching_ids = [hit["_source"]["job_id"] for hit in es_results['hits']['hits']]
        
        # If no matching documents, raise an exception
        if not matching_ids:
            raise HTTPException(status_code=404, detail="No matching jobs found in Elasticsearch")

        return matching_ids
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while searching in Elasticsearch: {str(e)}")


# Method to search in MySQL using the matching IDs
def search_in_mysql(matching_ids: List[str]):
    placeholders = ', '.join(['%s'] * len(matching_ids))
    mysql_query = f"""
        SELECT a.title, CONCAT('https://candidat.francetravail.fr/offres/recherche/detail/', a.internal_id) as link, 
               b.label as contract_type, 
               CASE WHEN c.max_monthly_salary IS NULL 
                    THEN CONCAT('à partir de ', c.min_monthly_salary, ' € par mois') 
                    ELSE CONCAT('de ', c.min_monthly_salary, ' € à ', c.max_monthly_salary, ' € par mois') 
               END as salary, 
               CASE WHEN d.name = '75' THEN 'PARIS' ELSE d.name END as city
        FROM job a
        JOIN job_contract b ON a.job_id = b.job_id
        JOIN salary c ON a.job_id = c.job_id
        JOIN cities d ON a.insee_code = d.insee_code
        WHERE a.job_id IN ({placeholders})
    """
    try:
        with get_db() as cursor:
            cursor.execute(mysql_query, matching_ids)  # Pass matching IDs to the MySQL query
            result = cursor.fetchall()  # Fetch the results from MySQL
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while querying MySQL: {str(e)}")


@app.post("/search/")
def search_jobs(payload: SearchPayload, db=Depends(get_db)):
    # Step 1: Search in Elasticsearch for matching job IDs
    matching_ids = search_in_elasticsearch(payload)
    
    # Step 2: Search in MySQL using the matching IDs
    result = search_in_mysql(matching_ids)
    
    return result


####  salary prediction
@app.get("/salary/{id:int}")
def get_salary(id):
    return ({"Salary class": str(getPrediction(id))})
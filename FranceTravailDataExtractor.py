import requests
import json
import os


#### Save credentials 
""" OUTPUT_DIR="C:/Users/medsa/Desktop/projet_DE"

d={
    "clientID":"$$$ to be filled",
    "key":"$$$$ to be filled"
} """

def saveCreadentials(OUTPUT_DIR,d):
    with open(os.path.join(OUTPUT_DIR,"clientCredentials.json"),"w") as idFile:
        json.dump(d,idFile)
        idFile.close()  

saveCreadentials(OUTPUT_DIR,d)

#### 0.get credentials

with open(os.path.join(OUTPUT_DIR,"clientCredentials.json"),"r") as idFile:
    id=json.load(idFile)

#;charset=UTF-8

headers={"Content-Type":"application/x-www-form-urlencoded"}
params={
    "grant_type":"client_credentials",
    "client_id":id["clientID"],
    "client_secret":id["key"],
    "scope":"api_offresdemploiv2"
}


#### 1.generate token

try:
    req=requests.post(url= "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire",
              headers= headers,params=params)
    req.raise_for_status()
except requests.exceptions.HTTPError as errh: 
    print("HTTP Error") 
    print(errh.args[0]) 


token=req.json()["access_token"]
token_type=req.json()["token_type"]
#### 2.query api
headers={
    "Accept": "application/json",
    "Authorization": token_type+" "+token
}

query=requests.get(url="https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search", headers= headers)

print(query.json())
query.headers
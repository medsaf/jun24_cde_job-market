# jun24_cde_job-market



1- Le fichier qui permet de requeter FranceTravail API est: FranceTravailDataExtractor.py

    1-a Pour tourner le code il faut au prealable creer une "clientID" et une "Key" en s'inscrivant sur France travail et en ajoutant l'api "offresdemploi"
    1-b Enregistrer le "clientID" et le "Key" dans un fichier "clientCredentials.json". 
    1-C clientCreadentials est dans .gitignore 


2-Pour accéder à la session Postman France_Travail.postman_collection.json il faut installer Postman puis Ctrl+O pour importer le fichier


2- Elastic search instance and uploading data
In order to save data we implemented an elastic search service coupled to logstash in order to automate data loading 
follow these steps to launch the service:
    - Go to Elasticsearch folder
    - docker compose up
    - one the console type: docker exec -it ls-container bash
    - then type: ./bin/logstash -f pipeline/pipeline.conf --config.reload.automatic true 
    the logstashah instance as well as the elastic search instance are loaded

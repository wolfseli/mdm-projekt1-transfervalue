# cd backend
# python -m flask --debug --app service run

import datetime
import os
import pickle
from pathlib import Path

import pandas as pd
from azure.storage.blob import BlobServiceClient
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# init app, load model from storage
print("*** Init and load model ***")
if 'AZURE_STORAGE_CONNECTION_STRING' in os.environ:
    azureStorageConnectionString = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    blob_service_client = BlobServiceClient.from_connection_string(azureStorageConnectionString)

    print("fetching blob containers...")
    containers = blob_service_client.list_containers(include_metadata=True)
    for container in containers:
        existingContainerName = container['name']
        print("checking container " + existingContainerName)
        if existingContainerName.startswith("transfervalue-model-"):
            parts = existingContainerName.split("-")
            print(parts)
            suffix = 1
            if (len(parts) == 3):
                newSuffix = int(parts[-1])
                if (newSuffix > suffix):
                    suffix = newSuffix

    container_client = blob_service_client.get_container_client("transfervalue-model-" + str(suffix))
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        print("\t" + blob.name)

    # Download the blob to a local file
    Path("../model").mkdir(parents=True, exist_ok=True)
    download_file_path = os.path.join("../model", "GradientBoostingRegressor.pkl")
    print("\nDownloading blob to \n\t" + download_file_path)

    with open(file=download_file_path, mode="wb") as download_file:
         download_file.write(container_client.download_blob(blob.name).readall())

else:
    print("CANNOT ACCESS AZURE BLOB STORAGE - Please set connection string as env variable")
    print(os.environ)
    print("AZURE_STORAGE_CONNECTION_STRING not set")    

file_path = Path(".", "../model/", "GradientBoostingRegressor.pkl")
with open(file_path, 'rb') as fid:
    model = pickle.load(fid)

print("*** Init Flask App ***")
app = Flask(__name__)
cors = CORS(app)
app = Flask(__name__, static_url_path='/', static_folder='../frontend')

# API Endpoint für Index Page
@app.route("/")
def indexPage():
     return send_file("../frontend/index.html")  

# API Endpoint für Vorhersage
@app.route("/api/predict")
def predict():
    # Input Values erhalten
    Comp_eng = request.args.get('Comp_eng', type=int)
    Age = request.args.get('age', type=int)
    Min = request.args.get('minutes' , type=int)
    Gls = request.args.get('goals' , type=int)
    Ast = request.args.get('assists' , type=int)
    xG = request.args.get('xG', type=float)
    xAG = request.args.get('xAG', type=float)
    npxG_xAG = request.args.get('npxG_xAG', type=float)
    PrgC = request.args.get('PrgC', type=int)
    PrgP = request.args.get('PrgP', type=int)
    PrgR = request.args.get('PrgR', type=int)
    
    
    # Daten für Vorhersage vorbereiten
    data = {"Comp_eng": [Comp_eng], 'Age': [Age], 'Min': [Min], 'Gls': [Gls], 'Ast': [Ast], 'xG': [xG], 'xAG': [xAG], 'npxG+xAG': [npxG_xAG], 'PrgC': [PrgC], 'PrgP': [PrgP], 'PrgR': [PrgR]}
    df = pd.DataFrame(data)
        
    # Vorhersage berechnen
    predicted_value = model.predict(df)

    # Vorhersage schöner formatieren / Ohne Kommastellen und mit Apostroph
    predicted_value = ["{:,}".format(int(predicted_value[0])).replace(",", "'")]
    
    # Vorhersage zurückgeben
    response = {'Value': predicted_value[0]}
    
    return jsonify(response)


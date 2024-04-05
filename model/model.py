# cd model
# python model.py -u 'mongodb+srv://<user>:<password>@mdmmongodbwolfseli.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000' -d 'players' -c 'players'

print("--------------------")
print("Daten aus Azure Cosmos DB abrufen und vorbereiten")
print("--------------------")

import argparse
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from pymongo import MongoClient

parser = argparse.ArgumentParser(description='Import data from Azure Cosmos DB')
parser.add_argument('-u', '--uri', required=True, help="Azure Cosmos DB connection string")
parser.add_argument('-d', '--database', required=True, help="Database name")
parser.add_argument('-c', '--collection', required=True, help="Collection name")
args = parser.parse_args()

mongo_uri = args.uri
mongo_db = args.database
mongo_collection = args.collection

# Azure Cosmos DB verbindung
client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

# Alle Dokumente aus der Sammlung abrufen
cursor = collection.find({})

# Documents in eine Liste von Dictionaries konvertieren
data = list(cursor)

# MongoDB connection schliessen
client.close()

# Erstellen eines DataFrames aus der Liste von Dictionaries
df = pd.DataFrame(data)

# Anzahl der abgerufenen Dokumente anzeigen
print("Number of documents fetched:", len(df))

# Entfernen der '_id' Spalte
df.drop(columns=['_id'], inplace=True)

# Informationen zum DataFrame anzeigen
print(df.info())

# Berechnung der Korrelation
correlation = df.corr()
print(correlation)

plt.figure(figsize=(16, 6))
heatmap = sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()

# Spalten entfernen, die nicht für die Modellierung benötigt werden
df = df.drop('90s', axis=1)
df = df.drop('MP', axis=1)
df = df.drop('G+A', axis=1)
df = df.drop('G-PK', axis=1)
df = df.drop('npxG', axis=1)
df = df.drop('Starts', axis=1)
df = df.drop('PK', axis=1)
df = df.drop('PKatt', axis=1)
df = df.drop('CrdY', axis=1)
df = df.drop('CrdR', axis=1)
df = df.drop('Comp_de', axis=1)
df = df.drop('Comp_es', axis=1)
df = df.drop('Comp_fr', axis=1)
df = df.drop('Comp_it', axis=1)

# Plot nochmals anzeigen
correlation = df.corr()
plt.figure(figsize=(16, 6))
heatmap = sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()

print("--------------------")
print("Model trainieren und testen")
print("--------------------")

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Daten in Features und Zielvariablen aufteilen
X = df.drop('Value', axis=1)
y = df['Value']

# Aufteilen der Daten in Trainings- und Testdaten
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Modell trainieren und testen
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest Regression": RandomForestRegressor(),
    "Gradient Boosting Regression": GradientBoostingRegressor(),
    "SVR": SVR(),
    "KNN": KNeighborsRegressor()
}

for modelName, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"Model: {modelName}")
    print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred)}")
    print(f"R2 Score: {r2_score(y_test, y_pred)}")
    print("\n")

# Gradient Boosting Regression hat den besten R2 Score und den niedrigsten Mean Squared Error
gbr = GradientBoostingRegressor(random_state=42)
gbr.fit(X_train, y_train)

print("--------------------")
print("Demo: Vorhersage für einen Spieler")
print("--------------------")

# Beispiel Spieler
player = {
    "Comp_eng": 1, 
    "Age": 28,
    "Min": 1823,
    "Gls": 4,
    "Ast": 1,
    "xG": 4.4,
    "xAG": 1.4,
    "npxG+xAG": 5.8,
    "PrgC": 58,
    "PrgP": 46,
    "PrgR": 83,
}

# Vorhersage für den Spieler
player_df = pd.DataFrame([player])
prediction = int(gbr.predict(player_df)[0])
print(f"Predicted Value: {prediction}")

#  ----------------- Save Model -----------------

# Save To Disk
import pickle

# save the classifier
with open('GradientBoostingRegressor.pkl', 'wb') as fid:
    pickle.dump(gbr, fid)    

# load it again
with open('GradientBoostingRegressor.pkl', 'rb') as fid:
    gbr_loaded = pickle.load(fid)
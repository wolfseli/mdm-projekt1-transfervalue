# cd /downloads
# python .\mongo_import.py -c players -i ./file.jl -u 'mongodb+srv://<user>:<password>@mdmmongodbwolfseli.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000'

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor

from pymongo import MongoClient

from pathlib import Path

def to_document(base_dir, item):
    try:
        doc = {
            "Comp_de": item["Comp_de"],
            "Comp_eng": item["Comp_eng"],
            "Comp_es": item["Comp_es"],
            "Comp_fr": item["Comp_fr"],
            "Comp_it": item["Comp_it"],
            "Age": item["Age"],
            "MP": item["MP"], 
            "Min": item["Min"],
            "90s": item["90s"],
            "Gls": item["Gls"],
            "Ast": item["Ast"],
            "G+A": item["G+A"],
            "G-PK": item["G-PK"],
            "PK": item["PK"],
            "PKatt": item["PKatt"],
            "CrdY": item["CrdY"],
            "CrdR": item["CrdR"],
            "xG": item["xG"],
            "npxG": item["npxG"],
            "xAG": item["xAG"],
            "npxG+xAG": item["npxG+xAG"],
            "PrgC": item["PrgC"],
            "PrgP": item["PrgP"],
            "PrgR": item["PrgR"],
            "Value": item["Value"],
            "Starts": item["Starts"],
        }
        return doc
            
    except Exception as e:
        print("Error processing item:", e)
        return None

class JsonLinesImporter:

    def __init__(self, file, mongo_uri, batch_size=30, db='players', collection='players'):
        self.file = file
        self.base_dir = os.path.dirname(file)
        self.batch_size = batch_size
        self.client = MongoClient(mongo_uri)
        self.db = db
        self.collection = collection

    def read_lines(self):
            with open(self.file, encoding='UTF-8') as f:
                batch = []
                for line in f:
                    batch.append(json.loads(line))
                    if len(batch) == self.batch_size:
                        yield batch
                        batch.clear()
                yield batch

    def save_to_mongodb(self):
            db = self.client[self.db]
            collection = db[self.collection]
            # bestehende Daten löschen
            collection.delete_many({})
            for idx, batch in enumerate(self.read_lines()):
                print("inserting batch", idx)
                collection.insert_many(self.prepare_documents(batch))

    def prepare_documents(self, batch):
        documents = []
        with ProcessPoolExecutor() as executor:
            for document in executor.map(to_document, [self.base_dir] * len(batch), batch):
                if document is not None:
                    documents.append(document)
        return documents

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--uri', required=True, help="mongodb uri with username/password")
    parser.add_argument('-i', '--input', required=True, help="input file in JSON Lines format")
    parser.add_argument('-c', '--collection', required=True, help="name of the mongodb collection where the tracks should be stored")
    args = parser.parse_args()
    importer = JsonLinesImporter(args.input, collection=args.collection, mongo_uri=args.uri)
    importer.save_to_mongodb()

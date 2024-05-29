from pymongo import MongoClient, InsertOne
import csv
import os
from dotenv import load_dotenv
import glob
import pandas as pd


def ukhsa_import_geno_csv(inputDir):

    load_dotenv()

    MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client=MongoClient(host=["mongodb:27017"],
                       username=MONGO_INITDB_ROOT_USERNAME,
                       password=MONGO_INITDB_ROOT_PASSWORD)


    inputDir = inputDir.rstrip('/')
    dateDir = inputDir.split('/')[-3:]
    dashDate = dateDir[0] + "-" + dateDir[1] + "-" + dateDir[2]

    db = client.tb
    requesting = []

    input_csv = dashDate + "-genotyping_resistance.csv"

    header = pd.read_csv(os.path.join(inputDir, input_csv), index_col=False, nrows=0).columns.tolist()

    with open(os.path.join(inputDir, input_csv), 'r') as infile:
        reader = csv.DictReader(infile)
        for elem in reader:
            row = {}
            for field in header:
                row["ukhsa " + field] = elem[field]
            collection_name = str(row["ukhsa MiseqOutput"]) + "_ukhsa"
            requesting.append(InsertOne(row))
            result = db[collection_name].bulk_write(requesting)
            requesting.clear()

    client.close()


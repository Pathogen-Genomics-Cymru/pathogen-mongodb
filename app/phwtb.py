from pymongo import MongoClient, InsertOne
import csv
import os
from dotenv import load_dotenv
import glob
import pandas as pd

def phwtb_import(inputDir):

    load_dotenv()

    MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client=MongoClient(host=["mongodb:27017"],
                       username=MONGO_INITDB_ROOT_USERNAME,
                       password=MONGO_INITDB_ROOT_PASSWORD)


    inputDir = inputDir.rstrip('/')
    runID = inputDir.split('/')[-1]
    runIDelem = runID.split('_')
    shortrunID = str(runIDelem[0] + "_" + runIDelem[1])

    collection_name = shortrunID + "_phw"

    db = client.tb
    requesting = []

    input_csv = shortrunID + "_interim.csv"

    header = ["Accession Number", "Episode Number", "Mykrobe Species ID", "Mykrobe Species %", "Mykrobe Median", "Mykrobe Status", "PHW Basepairs", "PHW QC status", "Kraken Species ID", "Kraken species %", "Kraken Status", "NOTES", "LIMS Interim Species: TEXT TO REPORT", "LIMS Interim Rif Resistance: TEXT TO REPORT", "LIMS Interim Izh resistance: TEXT TO REPORT", "COMMENTS TO INCLUDE IN LIMS", "COMMENTS TO PENGU AND WCM"]


    header = pd.read_csv(os.path.join(inputDir, input_csv), index_col=False, nrows=0).columns.tolist()

    with open(os.path.join(inputDir, input_csv), 'r') as infile:
        reader = csv.DictReader(infile)
        for elem in reader:
            row = {}
            for field in header:
                row["PHW " + field] = elem[field]
            requesting.append(InsertOne(row))

    result = db[collection_name].bulk_write(requesting)
    client.close()

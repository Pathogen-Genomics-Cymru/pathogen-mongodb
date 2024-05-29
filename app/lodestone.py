from pymongo import MongoClient, InsertOne
import json
import os
from dotenv import load_dotenv
import glob


def lodestone_import(inputDir):

    load_dotenv()

    MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client=MongoClient(host=["mongodb:27017"],
                       username=MONGO_INITDB_ROOT_USERNAME,
                       password=MONGO_INITDB_ROOT_PASSWORD)


    inputDir = inputDir.rstrip('/')
    runID = inputDir.split('/')[-1]
    runIDelem = runID.split('_')
    shortrunID = runIDelem[0] + "_" + runIDelem[1]

    collection_name = shortrunID + "_lodestone"

    db = client.tb
    requesting = []

    include_report = glob.glob(os.path.join(inputDir, "*/*_report.json"), recursive=True)
    exclude_kraken = glob.glob(os.path.join(inputDir, "*/*_kraken_report.json"), recursive=True)
    exclude_afanc = glob.glob(os.path.join(inputDir, "*/*_afanc_report.json"), recursive=True)

    report_list = list(set(include_report) - set(exclude_kraken) - set(exclude_afanc))

    for reportdir in report_list:
        filename = os.path.basename(reportdir)
        with open(os.path.join(reportdir), 'r') as infile:
            myDict = json.loads(infile.read())
        for key in list(myDict):
            myDict["lodestone " + key] = myDict.pop(key)
        myDict["lodestone filename"] = str(filename)
        requesting.append(InsertOne(myDict))

    result = db[collection_name].bulk_write(requesting)
    client.close()

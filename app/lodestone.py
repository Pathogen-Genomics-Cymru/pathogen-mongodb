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

    db = client.tb
    requesting = []

    include_report = glob.glob(os.path.join(inputDir, sample, "*_report.json"))
    exclude_kraken = glob.glob(os.path.join(inputDir, sample, "*_kraken_report.json"))

    report_list = list(set(include_report) - set(exclude_kraken))

    for sample in os.listdir(inputDir):
        for filename in report_list:
            with open(os.path.join(inputDir, sample, filename), 'r') as infile:
                myDict = json.loads(infile.read())
                for key in list(myDict):
                    myDict["lodestone " + key] = myDict.pop(key)
                requesting.append(InsertOne(myDict))

    result = db[shortrunID].bulk_write(requesting)
    client.close()

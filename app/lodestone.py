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

    print (inputDir)
    print (runID)

    db = client.tb
    collection = db.runID
    requesting = []

    for sample in os.listdir(inputDir):
        print (sample)
        for filename in glob.glob(os.path.join(inputDir, sample, "*_report.json")):
            print (filename)
            with open(os.path.join(inputDir, sample, filename), 'r') as infile:
                myDict = json.loads(infile.read())
                requesting.append(InsertOne(myDict))

    result = collection.bulk_write(requesting)
    client.close()

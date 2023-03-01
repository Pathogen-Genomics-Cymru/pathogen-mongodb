from pymongo import MongoClient
from dotenv import load_dotenv
import os
import csv


def testconnection():
    """Tests connection to MongoDB, prints version if successful"""

    load_dotenv()

    MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client=MongoClient(host=["mongodb:27017"],
                       username=MONGO_INITDB_ROOT_USERNAME,
                       password=MONGO_INITDB_ROOT_PASSWORD)

    try:
        print ("server version:", client.server_info()["version"])
    except:
        print ("Cannot connect to MongoDB")


def create_tb_csv():
    """Create output tb csv"""

    load_dotenv()

    MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client=MongoClient(host=["mongodb:27017"],
                       username=MONGO_INITDB_ROOT_USERNAME,
                       password=MONGO_INITDB_ROOT_PASSWORD)

    db = client.tb
    collection_list = db.list_collection_names()

    header = ["_id", "PHW Accession Number", "PHW Episode Number", "PHW Mykrobe Species ID", "PHW Mykrobe Species %", "PHW Mykrobe Median", "PHW Mykrobe Status", "PHW PHW Basepairs", "PHW PHW QC status", "PHW Kraken Species ID", "PHW Kraken species %", "PHW Kraken Status", "PHW NOTES", "PHW LIMS Interim Species: TEXT TO REPORT", "PHW LIMS Interim Rif Resistance: TEXT TO REPORT", "PHW LIMS Interim Izh resistance: TEXT TO REPORT", "PHW COMMENTS TO INCLUDE IN LIMS", "PHW COMMENTS TO PENGU AND WCM"]

    with open('/data/test-data/phwtest.csv', 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for collect in collection_list:
            for post in db[collect].find():
                writer.writerow(post)

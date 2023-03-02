from pymongo import MongoClient
from dotenv import load_dotenv
import os
import csv
import pandas as pd
from collections import defaultdict

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
    print (collection_list)

    d = defaultdict(list)
    for item in collection_list:
        shortrunID = "_".join(item.split("_")[:2])
        print (shortrunID)
        lenrunID = len(shortrunID)
        d[item[:lenrunID]].append(item)
    print(dict(d))

    phw_speciation_fields = ["PHW Accession Number", "PHW Episode Number", "PHW Mykrobe Species ID", "PHW Mykrobe Species %", "PHW Kraken Species ID", "PHW Kraken species %"]

    # speciation csv
    for key, value in d.items():
        phw_df = pd.DataFrame()
        lodestone_df = pd.DataFrame()
        ukhsa_df = pd.DataFrame()
        print (key)
        for nested_val in value:
            print (nested_val)
            if nested_val.endswith("_phw"):
                phw_df = pd.DataFrame(list(db[nested_val].find()))
                phw_df = phw_df.drop(columns=[col for col in phw_df if col not in phw_speciation_fields])

                phw_csv_name = str(nested_val) + "_speciation.csv"
                phw_df.to_csv(phw_csv_name)

            if nested_val.endswith("_lodestone"):
                lodestone_df = pd.json_normalize(list(db[nested_val].find()), max_level=3)

                lodestone_csv_name = str(nested_val) + ".csv"
                lodestone_df.to_csv(lodestone_csv_name)


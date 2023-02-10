from pymongo import MongoClient
from dotenv import load_dotenv
import os


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

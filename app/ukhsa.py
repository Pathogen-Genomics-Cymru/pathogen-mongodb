from pymongo import MongoClient, InsertOne
import csv
import os
from dotenv import load_dotenv
import glob


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

    header = ["Pipeline_date", "GUUID", "Accession", "Episode", "MiseqOutput", "Total_million_reads", "Ref_coverage_pct", "Human_pct", "Species", "Lineage", "Mykrobe_species_pct", "Median_species", "type_AK", "type_CAP", "type_CIP", "type_EMB", "type_INH", "type_KAN", "type_MOX", "type_OFX", "type_PZA", "type_RIF", "type_SM", "type_SM-AG", "type_QUI"]

    with open(os.path.join(inputDir, input_csv), 'r') as infile:
        reader = csv.DictReader(infile)
        for elem in reader:
            row = {}
            for field in header:
                row["ukhsa " + field] = elem[field]
            shortrunID = str(row["ukhsa MiseqOutput"])
            requesting.append(InsertOne(row))
            result = db[shortrunID].bulk_write(requesting)
            requesting.clear()

    client.close()


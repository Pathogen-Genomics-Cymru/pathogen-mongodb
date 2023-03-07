from pymongo import MongoClient
from dotenv import load_dotenv
import os
import csv
import pandas as pd
import numpy as np
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

    d = defaultdict(list)
    for item in collection_list:
        shortrunID = "_".join(item.split("_")[:2])
        print (shortrunID)
        lenrunID = len(shortrunID)
        d[item[:lenrunID]].append(item)
    print(dict(d))

    phw_speciation_fields = ["PHW Accession Number", "PHW Episode Number", "PHW Mykrobe Species ID", "PHW Kraken Species ID"]
    lodestone_speciation_fields = ["PHW Accession Number", "PHW Episode Number", "lodestone top_hit.name"]
    ukhsa_speciation_fields = ["PHW Accession Number", "PHW Episode Number", "MiseqOutput", "ukhsa Species"]

    phw_resistance_fields = ["PHW Accession Number", "PHW Episode Number", "PHW LIMS Interim Rif Resistance: TEXT TO REPORT", "PHW LIMS Interim Izh resistance: TEXT TO REPORT"]
    lodestone_resistance_fields = ["PHW Accession Number", "PHW Episode Number", "lodestone data.EFFECTS.CAP", "lodestone data.EFFECTS.EMB", "lodestone data.EFFECTS.INH", "lodestone data.EFFECTS.LEV", "lodestone data.EFFECTS.MXF", "lodestone data.EFFECTS.PZA", "lodestone data.EFFECTS.RIF", "lodestone data.EFFECTS.STM"]
    ukhsa_resistance_fields = ["PHW Accession Number", "PHW Episode Number", "MiseqOutput", "ukhsa type_MOX", "ukhsa type_INH", "ukhsa type_SM", "ukhsa type_EMB", "ukhsa type_RIF", "ukhsa type_AK", "ukhsa type_CAP", "ukhsa type_CIP", "ukhsa type_KAN", "ukhsa type_OFX", "ukhsa type_PZA", "ukhsa type_QUI"]

    # speciation and resistance csv
    for key, value in d.items():

        phw_df = pd.DataFrame()
        lodestone_df = pd.DataFrame()
        ukhsa_df = pd.DataFrame()
        phw_species = pd.DataFrame()
        lodestone_species = pd.DataFrame()
        ukhsa_species = pd.DataFrame()
        phw_resistance = pd.DataFrame()
        lodestone_resistance = pd.DataFrame()
        ukhsa_resistance = pd.DataFrame()

        for nested_val in value:

            if nested_val.endswith("_phw"):

                phw_df = pd.DataFrame(list(db[nested_val].find()))

                phw_df['PHW Accession Number'] = phw_df['PHW Accession Number'].map(lambda x: x.lstrip('^CON-'))
                phw_df['PHW Episode Number'] = phw_df['PHW Episode Number'].map(lambda x: x and x.lstrip('^CON-'))

                phw_species = phw_df.drop(columns=[col for col in phw_df if col not in phw_speciation_fields])

                phw_csv_species = str(nested_val) + "_speciation.csv"
                phw_species.to_csv(phw_csv_species)

                phw_resistance = phw_df.drop(columns=[col for col in phw_df if col not in phw_resistance_fields])

                phw_csv_resistance = str(nested_val) + "_resistance.csv"
                phw_resistance.to_csv(phw_csv_resistance)

            if nested_val.endswith("_lodestone"):

                lodestone_df = pd.json_normalize(list(db[nested_val].find()), max_level=3)

                lodestone_df['lodestone filename'] = lodestone_df['lodestone filename'].str.replace('_', '-')

                lodestone_df['PHW Accession Number'] = lodestone_df['lodestone filename'].str.split('-').str.get(1)
                lodestone_df['PHW Episode Number'] = lodestone_df['lodestone filename'].str.split('-').str.get(2)

                lodestone_df["PHW Accession Number"] = lodestone_df.apply(lambda x: x['PHW Accession Number'].replace('CON', str(x['PHW Episode Number'])), axis=1)

                lodestone_df.drop('lodestone filename', axis=1, inplace=True)

                lodestone_df['PHW Episode Number'] = lodestone_df['PHW Episode Number'].astype('object')

                lodestone_species = lodestone_df.drop(columns=[col for col in lodestone_df if col not in lodestone_speciation_fields])
                lodestone_csv_species = str(nested_val) + "_speciation.csv"
                lodestone_species.to_csv(lodestone_csv_species)

                lodestone_resistance = lodestone_df.drop(columns=[col for col in lodestone_df if col not in lodestone_resistance_fields])
                lodestone_csv_resistance = str(nested_val) + "_resistance.csv"
                lodestone_resistance.to_csv(lodestone_csv_resistance)

            if nested_val.endswith("_ukhsa"):

                ukhsa_df = pd.DataFrame(list(db[nested_val].find()))

                ukhsa_df = ukhsa_df.rename(columns={'ukhsa Accession': 'PHW Accession Number', 'ukhsa Episode': 'PHW Episode Number', 'ukhsa MiseqOutput' : 'MiseqOutput'})

                ukhsa_species = ukhsa_df.drop(columns=[col for col in ukhsa_df if col not in ukhsa_speciation_fields])
                ukhsa_csv_species = str(nested_val) + "_speciation.csv"
                ukhsa_species.to_csv(ukhsa_csv_species)

                ukhsa_resistance = ukhsa_df.drop(columns=[col for col in ukhsa_df if col not in ukhsa_resistance_fields])
                ukhsa_csv_resistance = str(nested_val) + "_resistance.csv"
                ukhsa_resistance.to_csv(ukhsa_csv_resistance)

        species_df = ukhsa_species.merge(phw_species, on=['PHW Accession Number', 'PHW Episode Number'], how='left').merge(lodestone_species,  on=['PHW Accession Number', 'PHW Episode Number'], how='left')
        species_csv_name = str(key) + "_speciation.csv"
        species_df.to_csv(species_csv_name)

        resistance_df = ukhsa_resistance.merge(phw_resistance, on=['PHW Accession Number', 'PHW Episode Number'], how='left').merge(lodestone_resistance,  on=['PHW Accession Number', 'PHW Episode Number'], how='left')
        resistance_csv_name = str(key) + "_resistance.csv"
        resistance_df.to_csv(resistance_csv_name)

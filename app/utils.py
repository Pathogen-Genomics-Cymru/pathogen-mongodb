from pymongo import MongoClient
from dotenv import load_dotenv
import glob
import os
import csv
import pandas as pd
import numpy as np
from collections import defaultdict
import difflib

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


def same_merge(x): return ','.join(x[x.notnull()].astype(str))


def create_tb_csv(noLineage):
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
        lenrunID = len(shortrunID)
        d[item[:lenrunID]].append(item)
    print(dict(d))

    phw_speciation_fields = ["PHW Accession Number", "PHW Episode Number", "PHW Mykrobe Species ID", "PHW Mykrobe Species %", "PHW Kraken Species ID", "PHW Kraken species %"]
    lodestone_speciation_fields = ["PHW Accession Number", "PHW Episode Number", "lodestone top_hit.name", "lodestone top_hit.phylogenetics.species", "lodestone error"]
    ukhsa_speciation_fields = ["PHW Accession Number", "PHW Episode Number", "MiseqOutput", "ukhsa Species", "ukhsa Mykrobe_species_pct", "ukhsa Lineage"]

    #phw_resistance_fields = ["PHW Accession Number", "PHW Episode Number", "PHW LIMS Interim Rif Resistance: TEXT TO REPORT", "PHW LIMS Interim Izh resistance: TEXT TO REPORT"]
    #lodestone_resistance_fields = ["PHW Accession Number", "PHW Episode Number", "lodestone data.EFFECTS.CAP", "lodestone data.EFFECTS.EMB", "lodestone data.EFFECTS.INH", "lodestone data.EFFECTS.LEV", "lodestone data.EFFECTS.MXF", "lodestone data.EFFECTS.PZA", "lodestone data.EFFECTS.RIF", "lodestone data.EFFECTS.STM"]
    #ukhsa_resistance_fields = ["PHW Accession Number", "PHW Episode Number", "MiseqOutput", "ukhsa type_MOX", "ukhsa type_INH", "ukhsa type_SM", "ukhsa type_EMB", "ukhsa type_RIF", "ukhsa type_AK", "ukhsa type_CAP", "ukhsa type_CIP", "ukhsa type_KAN", "ukhsa type_OFX", "ukhsa type_PZA", "ukhsa type_QUI"]


    mycoTaxMap = pd.read_csv('mycoTaxMap.csv')
    old_spec = mycoTaxMap['name_old'].tolist()
    new_spec = mycoTaxMap['name_new'].tolist()

    lineageMap = pd.read_csv('lineagemap.csv')
    afanc_lineage = lineageMap['afanc_lineage'].tolist()
    mykrobe_lineage = lineageMap['mykrobe_compass_lineage'].tolist()

    # speciation and resistance csv
    for key, value in d.items():

        phw_df = pd.DataFrame()
        lodestone_df = pd.DataFrame()
        ukhsa_df = pd.DataFrame()
        phw_species = pd.DataFrame()
        lodestone_species = pd.DataFrame()
        ukhsa_species = pd.DataFrame()
        #phw_resistance = pd.DataFrame()
        #lodestone_resistance = pd.DataFrame()
        #ukhsa_resistance = pd.DataFrame()

        for nested_val in value:

            if nested_val.endswith("_phw"):

                phw_df = pd.DataFrame(list(db[nested_val].find()))

                phw_df['PHW Accession Number'] = phw_df['PHW Accession Number'].map(lambda x: x.lstrip('^CON-'))
                phw_df['PHW Episode Number'] = phw_df['PHW Episode Number'].map(lambda x: x and x.lstrip('^CON-'))

                phw_species = phw_df.drop(columns=[col for col in phw_df if col not in phw_speciation_fields])

                #phw_resistance = phw_df.drop(columns=[col for col in phw_df if col not in phw_resistance_fields])

            if nested_val.endswith("_lodestone"):

                lodestone_df = pd.json_normalize(list(db[nested_val].find()), max_level=3)

                lodestone_df['lodestone filename'] = lodestone_df['lodestone filename'].str.replace('_', '-')

                lodestone_df['PHW Accession Number'] = lodestone_df['lodestone filename'].str.split('-').str.get(1)
                lodestone_df['PHW Episode Number'] = lodestone_df['lodestone filename'].str.split('-').str.get(2)

                lodestone_df["PHW Accession Number"] = lodestone_df.apply(lambda x: x['PHW Accession Number'].replace('CON', str(x['PHW Episode Number'])), axis=1)

                lodestone_df.drop('lodestone filename', axis=1, inplace=True)

                lodestone_df['PHW Episode Number'] = lodestone_df['PHW Episode Number'].astype('object')

                lodestone_df = lodestone_df.rename(columns = { i: "lodestone top_hit.phylogenetics.species" for i in lodestone_df.columns if i.startswith("lodestone top_hit.phylogenetics.species") } )

                lodestone_species = lodestone_df.drop(columns=[col for col in lodestone_df if col not in lodestone_speciation_fields])

                lodestone_species = lodestone_species.groupby(level=0, axis=1).apply(lambda x: x.apply(same_merge, axis=1))

                match = []
                lineage_match = []
                lode_spec = lodestone_species['lodestone top_hit.name'].tolist()

                if noLineage:
                    for elem in lode_spec:
                        try:
                            match_string = difflib.get_close_matches(str(elem), new_spec, n=1)[0]
                            match_index = new_spec.index(match_string)
                            old_match = old_spec[int(match_index)]
                            match.append(' '.join(old_match.split()[:2]))
                        except:
                            match.append('')
                    lodestone_species['lodestone normalised species'] = match
                else:
                    for elem in lode_spec:
                        if elem in afanc_lineage:
                            match_index = afanc_lineage.index(elem)
                            mykrobe_match = mykrobe_lineage[int(match_index)]
                            lineage_match.append(mykrobe_match)
                            if elem.startswith("Mycobacterium tuberculosis lineage"):
                                match.append("Mycobacterium tuberculosis")
                            else:
                                try:
                                    match_string = difflib.get_close_matches(str(elem), new_spec, n=1)[0]
                                    match_index = new_spec.index(match_string)
                                    old_match = old_spec[int(match_index)]
                                    match.append(' '.join(old_match.split()[:2]))
                                except:
                                    match.append('')
                        else:
                            lineage_match.append('')
                            try:
                                match_string = difflib.get_close_matches(str(elem), new_spec, n=1)[0]
                                match_index = new_spec.index(match_string)
                                old_match = old_spec[int(match_index)]
                                match.append(' '.join(old_match.split()[:2]))
                            except:
                                match.append('')
                    lodestone_species['lodestone normalised species'] = match
                    lodestone_species['lodestone mykrobe format lineage'] = lineage_match

                #lodestone_resistance = lodestone_df.drop(columns=[col for col in lodestone_df if col not in lodestone_resistance_fields])

            if nested_val.endswith("_ukhsa"):

                ukhsa_df = pd.DataFrame(list(db[nested_val].find()))

                ukhsa_df = ukhsa_df.rename(columns={'ukhsa Accession': 'PHW Accession Number', 'ukhsa Episode': 'PHW Episode Number', 'ukhsa MiseqOutput' : 'MiseqOutput'})

                ukhsa_species = ukhsa_df.drop(columns=[col for col in ukhsa_df if col not in ukhsa_speciation_fields])

                match=[]
                ukhsa_spec = ukhsa_species['ukhsa Species'].tolist()

                for elem in ukhsa_spec:
                    try:
                        match.append(difflib.get_close_matches(elem, old_spec, n=1)[0])
                    except:
                        match.append('')

                ukhsa_species['ukhsa normalised species'] = match

                #ukhsa_resistance = ukhsa_df.drop(columns=[col for col in ukhsa_df if col not in ukhsa_resistance_fields])

        try:
            species_df = ukhsa_species.merge(phw_species, on=['PHW Accession Number', 'PHW Episode Number'], how='left').merge(lodestone_species,  on=['PHW Accession Number', 'PHW Episode Number'], how='left')

            species_df.drop_duplicates(subset=['PHW Accession Number'], inplace=True)

            species_csv_name = str(key) + "_speciation.csv"
            species_df.to_csv(species_csv_name)

            #resistance_df = ukhsa_resistance.merge(phw_resistance, on=['PHW Accession Number', 'PHW Episode Number'], how='left').merge(lodestone_resistance,  on=['PHW Accession Number', 'PHW Episode Number'], how='left')
            #resistance_csv_name = str(key) + "_resistance.csv"
            #resistance_df.to_csv(resistance_csv_name)

        except:
            print(str(key) + ": Error creating final speciation csv")


def species_group(inputDir):
    """Generate grouped csvs for speciation csvs"""

    print(inputDir)
    all_csvs = glob.glob(os.path.join(inputDir , "*_speciation.csv"))

    collect = []
    for csv in all_csvs:
        print (csv)
        df = pd.read_csv(csv, index_col=None, header=0)
        collect.append(df)

    all_species = pd.concat(collect, axis=0, ignore_index=True)

    species_match = all_species.loc[all_species['ukhsa normalised species'] == all_species['lodestone normalised species']]
    species_match = species_match[species_match.columns.difference(['ukhsa Species', 'ukhsa Mykrobe_species_pct', 'lodestone error', 'lodestone top_hit.name', 'lodestone top_hit.phylogenetics.species'])]

    species_diff = all_species.loc[~(all_species['ukhsa normalised species'] == all_species['lodestone normalised species'])]
    species_diff = species_diff[species_diff.columns.difference(['ukhsa Species', 'ukhsa Mykrobe_species_pct', 'lodestone error', 'lodestone top_hit.name', 'lodestone top_hit.phylogenetics.species'])]

    all_species.to_csv("all_samples.csv")
    species_match.to_csv("species_same.csv")
    species_diff.to_csv("species_diff.csv")

    #lineage_match = all_species.loc[all_species['ukhsa Lineage'] == all_species['lodestone mykrobe format lineage']]
    #lineage_match = lineage_match[lineage_match.columns.difference(['ukhsa Species', 'lodestone top_hit.name', 'ukhsa Lineage', 'lodestone mykrobe format lineage'])]

    #lineage_diff = all_species.loc[~(all_species['ukhsa Lineage'] == all_species['lodestone mykrobe format lineage'])]
    #lineage_diff = lineage_diff[lineage_diff.columns.difference(['ukhsa Species', 'lodestone top_hit.name', 'ukhsa Lineage', 'lodestone mykrobe format lineage'])]

    #lineage_match.to_csv("lineage_same.csv")
    #lineage_diff.to_csv("lineage_diff.csv")


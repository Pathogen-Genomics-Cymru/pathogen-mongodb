# pathogen-mongodb
![Build Status](https://github.com/Pathogen-Genomics-Cymru/pathogen-mongodb/workflows/build-push-quay/badge.svg)

## Introduction

Pathogen-mongodb is a containerised MongoDB service that is launched through [docker-compose](https://docs.docker.com/compose/). [MongoDB](https://www.mongodb.com) is a NoSQL, document-oriented database program, which uses JSON-like array structures for storing data. Pathogen-mongodb uses the [PyMongo](https://pymongo.readthedocs.io/en/stable/) python driver to communicate with the MongoDB database.

There are two containers in the docker-compose stack (see `docker-compose.yml`):

1) Containerised MongoDB program
2) Python container to run `pathogen-mongodb.py` program utilising PyMongo

The `pathogen-mongodb.py` python application in the `app` directory imports output data from the PHW TB (CSV), UKHSA compass (CSV), and lodestone (JSON) pipelines into a MongoDB database, and can be used to generate csvs comparing the speciation and lineage results on a per run basis. Grouped csvs for all the runs can also be generated. 

The lodestone pipeline uses a more recent version of the NCBI taxonomy than the other pipelines, where Mycobacteriaceae is divided into the sub-genera: Mycobacterium, Mycolicibacterium, Mycolicibacter, Mycolicibacillus, and Mycobacteroides ([REF](https://www.frontiersin.org/articles/10.3389/fmicb.2018.00067/full)). Therefore, in order to make a comparison between the pipelines, a mapping file (`app/mycoTaxMap.csv`) is used to map the top species hit to the same taxonomy for UKHSA and lodestone (see the `ukhsa normalised species` and `lodestone normalised species` columns in the speciation csvs). Similarly, a mapping file for the lineages (`app/lineagemap.csv`) is used to the map the numerical lineages from lodestone (e.g. lineage 4.1) to the geographical lineages used in compass (e.g. European American).

To ensure persistence of data, the output data of the three pipelines, the MongoDB database files, and the `pathogen-mongodb.py` app are stored locally and accessed by the containers through bind mounts.

There is bridge network between the two containers allowing communication between `pathogen-mongodb.py` and MongoDB.

<img height="500" src="https://github.com/Pathogen-Genomics-Cymru/pathogen-mongodb/blob/main/pathogen-mongodb.png" />

## Usage
An install of docker and docker-compose is needed to run the service. See [here](https://docs.docker.com/desktop/install/linux-install/) for install instructions for docker. To install docker-compose:
```console
user@name:~/home$ sudo apt-get install docker-compose-plugin
```
Next make a clone of this repo:
```console
user@name:~/home$ git clone https://github.com/Pathogen-Genomics-Cymru/pathogen-mongodb.git
```

The `pathogen-mongodb.py` app uses the following output files from each pipeline:
* **runID/shortrunID_interim.csv** (PHW TB)
* **Year/Month/Day/Date-genotyping_resistance.csv** (UKHSA Compass)
* **runID/sampleID/sampleID_report.json** and **runID/sampleID/sampleID_kraken_report.json** (lodestone; there is a json for each sample)

Please note that for the PHW and lodestone results, the directory needs to be named after the full runID and for UKHSA the following date form is expected for the directory name: 2022/10-Oct/07.

Before starting the docker-compose service, define any volumes needed in the `docker-compose.yml`, by default the following are defined:
```
volumes:
      - ${PWD}/database:/data/db
      - ${PWD}/app:/data/app
      - ${PWD}/test-data:/data/test-data
```
The volumes are defined as `LocalPath:PathInContainer`. The volumes `${PWD}/database:/data/db` and `${PWD}/app:/data/app` can be left alone, these are the paths for the MongoDB database and the `pathogen-mongodb.py` app respectively. `${PWD}/test-data:/data/test-data` should be updated to reflect the path for the output data from the PHW TB, UKHSA compass, and lodestone pipelines. Note you can define multiple paths if you wish, e.g.
```
volumes:
      - ${PWD}/database:/data/db
      - ${PWD}/app:/data/app
      - ${PWD}/phw-results:/data/phw-results
      - ${PWD}/ukhsa-results:/data/ukhsa-results
      - ${PWD}/lodestone-results:/data/lodestone-results
```

A `user.env` file will also need to be defined for use by the mongoDB service, its path is set in `docker-compose.yml`
```
env_file:
      - ${PWD}/app/user.env
```
Create the `user.env` file with the username and password of your choice, it takes the following form:
```console
user@name:~/home/pathogen-mongodb/app$ cat user.env
MONGO_INITDB_ROOT_USERNAME: username
MONGO_INITDB_ROOT_PASSWORD: password
```

To start the docker-compose service, from the `pathogen-monogdb` directory run:
```console
user@name:~/home/pathogen-mongodb$ docker-compose up -d
```
The `-d` flag tells docker-compose to run the containers in detached mode in the background. To check the status of service:
```console
user@name:~/home/pathogen-mongodb$ docker ps -a
CONTAINER ID   IMAGE                                           COMMAND                  CREATED        STATUS        PORTS                                           NAMES
1ecdc6758c1c   quay.io/pathogen-genomics-cymru/pymongo:4.3.3   "tail -f /dev/null"      21 hours ago   Up 21 hours                                                   pymongo
938304f73185   mongo:4.4.19-rc0-focal                          "docker-entrypoint.s…"   21 hours ago   Up 21 hours   0.0.0.0:27017->27017/tcp, :::27017->27017/tcp   mongodb

```
To run `pathogen-mongodb.py` use `docker exec` to start a bash shell with the `pymongo` container, then navigate to `data/app` directory. From this directory you can run the `pathogen-mongodb.py` app:
```console
user@name:~/home/pathogen-mongodb$ docker exec -it pymongo bash
root@1ecdc6758c1c:/# cd data/app/
root@1ecdc6758c1c:/data/app# python3 pathogen-mongodb.py -h
usage: pathogen-mongodb.py [-h] [-l LODESTONEDIR] [-p PHWDIR] [-u UKHSADIR] [-c]

options:
  -h, --help            show this help message and exit
  -l LODESTONEDIR, --lodestone-dir LODESTONEDIR
                        Output directory from lodestone run
  -p PHWDIR, --phw-dir PHWDIR
                        Output directory for PHW results
  -u UKHSADIR, --ukhsa-dir UKHSADIR
                        Output directory for UKHSA results
  -c, --tb-csv          Create output csv
  -s SPECIESGROUP, --species-group SPECIESGROUP
                        Path to speciation csvs
  -n, --no-lineage      Use this flag for versions of lodestone before 0.9.7
```
The `-l`, `-p` and `-u` flags should be set to the paths for the results from the three pipelines, which will be imported into the MongoDB database. E.g. to import data from the three pipelines (note we're using the path in the container):
```console
root@1ecdc6758c1c:/data/app# python3 pathogen-mongodb.py -p /data/phw-results/RUNID -l /data/lodestone-results/RUNID -u /data/ukhsa-results/Year/Month/Day
```
To import data from multiple runs, use a while loop with a txt file with the list of runs to be imported, e.g.
```
while IFS= read -r line; do
    python3 pathogen-mongodb.py -p /data/phw-results/$line -l /data/lodestone-results/$line
done < runIDs.txt
```
The `-c` flag generates speciation csvs on a per run basis of all the runs in the MongoDB database. The `-s` flag can be used to generate csvs with grouped results from multiple speciation csvs.

E.g. using the `-c` flag:
```console
root@1ecdc6758c1c:/data/app# python3 pathogen-mongodb.py -c
```
will generate `shortrunID_speciation.csv` for each run. If there is missing data for a run (i.e. entries are only found for one or two of the three pipelines for a run), the csvs will not be produced for this run and you will see the following error message is generated:
```
shortrunID: Error creating final speciation csv
```

E.g. using the `-s` flag, set to the path where the `*_speciation.csv` are:
```
root@1ecdc6758c1c:/data/app# python3 pathogen-mongodb.py -s $(PWD)
```
will generate 3 csvs:
* `all_samples.csv` (all of the results from all *_speciation.csv)
* `species_same.csv` (samples whose normalised top species is in agreement)
* `species_diff.csv` (samples with differing normalised top species)

Currently all the csvs are written to `app` directory.

To spin down docker-compose:
```console
user@name:~/home/pathogen-mongodb$ docker-compose down
```

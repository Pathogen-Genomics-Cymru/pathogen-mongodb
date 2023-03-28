# pathogen-mongodb
![Build Status](https://github.com/Pathogen-Genomics-Cymru/pathogen-mongodb/workflows/build-push-quay/badge.svg)

## Introduction

Pathogen-mongodb is a containerised MongoDB service that is launched through [docker-compose](https://docs.docker.com/compose/). [MongoDB](https://www.mongodb.com) is a NoSQL, document-oriented database program, which uses JSON-like array structures for storing data. Pathogen-mongodb uses the  [PyMongo](https://pymongo.readthedocs.io/en/stable/) python driver to communicate with the MongoDB database.

There are two containers in the docker-compose stack:

1) Containerised MongoDB program
2) Python container to run pathogen-mongodb.py python program utilising PyMongo

The pathogen-mongodb.py python application imports output data from the PHW TB (CSV), UKHSA compass (CSV), and lodestone (JSON) pipelines into a MongoDB database, and can be used to create a comparison of the speciation and antimicrobial resistance results on a per run basis. The lodestone pipeline uses a more recent version of the NCBI taxonomy than the the other pipelines, therefore in order to make a comparison between the pipelines, a mapping file is used to map the pipelines to the same taxonomy.

To ensure persistence of data, the database files, pathogen-mongodb.py, and the pipeline output are stored locally and accessed by the containers through bind mounts.

There is bridge network between the two containers allowing communication between pathogen-mongodb.py and MongoDB.

<img height="500" src="https://github.com/Pathogen-Genomics-Cymru/pathogen-mongodb/blob/main/pathogen-mongodb.png" />

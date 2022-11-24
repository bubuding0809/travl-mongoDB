# TLM 2004 - Travl Database MongoDB Implementation

## Introduction

This repository contains all code and raw data required to initialize and operate a MongoDB implementation of our database

- **migration_data.zip** - contains all the raw data in json formated required to seed database, this raw data has been extract from our MySQL database that was implemented in the first half of our the project. Unzip this file to access the data.
- **migration.py** - This script contains all functions required to migrate all the raw json data from migration_data folder into a MongoDB database instance. Run this script after unzipping **migration_data.zip**.
- **transaction.py** - This script demostrates the use of MongoDB transactions to execute an ACID transaction for a flight ticket purchase use-case. This script is hardcoded to purhcase a flight ticket by user _"cl92lvec40000obt1t62zu8ca"_ and for flight _"ObjectId('636f976323bf341c1d810294')"_. Running this script will generate a new ticket document, a new passenger document and update the respective user and flight document to reflect the changes. Only run this script after the database has been initialized by running **migration.py**.
- **utils.py**, **generate_flights.py**, **generate_passenger_tickets.py** contains helper functions for the **migration.py** and **transaction.py**.
- **queries.ipynb** - This is a juypter note book that contains all our demostrated queries, only run this queries after database has been initialized.

## How to

1. Ensure python 3.6 and later is installed, then install create a virtual env for this project. Activate enviroment and install all dependencies.
   ```
   > python -m venv env
   > env/Scripts/activate
   > pip install -r requirements.txt
   ```
2. Unzip **migration_data.zip**
3. Rename **.env.example** to **.env**, replace the following to your own database connection url. A hosted version of our database is not avaiable as hosting a database of our size will require paid services. Hence it is recommend you create a local instance of MongoDB and test out our database implementation.
   ```
   DATABASE_URL = <YOUR DATABASE_URL>
   ```
4. Run **migration.py** to seed your database with all the raw data from **migration_data/**. This will take some time as our data size is rather large, raw data size of ~ 1.5GB.
   ```
   > python migration.py
   ```
5. Once migration has completed successfully, you may test the transactions with **transaction.py** and the queries through **queries.ipynb**

## Others

Incase of any technical issues, please email me (Ding Ruoqian) at 2100971@sit.singaporetech.edu.sg

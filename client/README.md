# Client Handler

## Overview
This module serves as the handler for experiment, which initiates database, loads initial data, performs client transactions and provides measurements at transaction and database level.

## Module Structure
* main.py
    * handle an experiment by:
        * load the initial data to database given database name, number of servers (cockroach specific argument), number of workers and batch size
        * run the experiment given experiment number 
        * output transaction measurements, transaction summary and database status at the end of the experiment
* experiments: 
    * experiment handler for both database implementations
    * interact with client handlers to perform client transactions 
    * output transaction measurements and database status 
* handlers
    * interact with transaction methods to perform client transactions
    * output transaction measurements 
* loaders
    * load initial data to databases upon start of the experiment


## Usage Examples for CockroachDB

### Load Database Schema and Reset Tables

```bash
cd $WORKSPACE/cockroachdb/scripts/prod
source init-database.sh  # Run this with caution
```

### Activate Virtual Environment using `Pipenv`

```bash
# Activate shell
cd $WORKSPACE/
pipenv shell
```

### Overview of Custom CLI

```bash
python -m client.main -h
```

### Load Initial Data with Specified Worker and Batch Size

```bash
# Load data into CockroachDB
NUM_SERVERS=4 ENV=prod PORTS=26262 python -m client.main -l --cockroachdb --workers 16 --batch-size 2999
```

### Run Experiment with Specified Number

```bash
# Run experiment no.5 on CockroachDB
NUM_SERVERS=4 ENV=prod PORTS=26262 python -m client.main -e --cockroachdb -n 5
```

> Caveat: initial database setup should be done differently to handle different node sizes

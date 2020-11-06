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
# Run the following line with caution
bash bootstrap.sh
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
ENV=prod python -m client.main -l --cockroachdb --workers 16 --batch-size 2999 --ports=26257 \
    --hosts xcnc35.comp.nus.edu.sg,xcnc36.comp.nus.edu.sg,xcnc37.comp.nus.edu.sg,xcnc38.comp.nus.edu.sg,,xcnc39.comp.nus.edu.sg
```

### Run Experiment with Specified Number

```bash
# Run experiment no.5 on CockroachDB
ENV=prod python -m client.main -e --cockroachdb -en 5 --ports=26257 \
    --hosts xcnc35.comp.nus.edu.sg,xcnc36.comp.nus.edu.sg,xcnc37.comp.nus.edu.sg,xcnc38.comp.nus.edu.sg
```

> Caveat: initial database setup should be done differently to handle different node sizes

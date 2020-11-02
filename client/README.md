# Client Handler

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
ENV=prod PORTS=26262 python -m client.main -l --cockroachdb --workers 16 --batch-size 2999
```

### Run Experiment with Specified Number

```bash
# Run experiment no.5 on CockroachDB
ENV=prod PORTS=26262 python -m client.main -e --cockroachdb -n 5
```

> Caveat: initial database setup should be done differently to handle different node sizes

# CockroachDB Client Handler

This module serves as the handler for experiment, which initiates database, loads initial data, performs client transactions and provides measurements at transaction and database level.

## Module Structure

- `main.py`, handles an experiment by:
    - Load the initial data to database given database name, number of servers (cockroach specific argument), number of workers and batch size
    - Run the experiment given experiment number 
    - Output transaction measurements, transaction summary and database status at the end of the experiment
- `experiments/`
    - Experiment handler for both database implementations
    - Interact with client handlers to perform client transactions 
    - Output transaction measurements and database status 
- `handlers/`
    - Interact with transaction methods to perform client transactions
    - Output transaction measurements 
- `loaders/`
    - Load initial data to databases upon start of the experiment

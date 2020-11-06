# Cassandra

## Getting Started

We assume Cassandra is already installed on each node, and is included in the PATH environment variable.

### Configure `cassandra.yaml`
Set cluster name:
```yaml
cluster_name: 'CS5424 GrpO'
```
Set addresses of bootstrapping points
```yaml
seed_provider:
    - class_name: org.apache.cassandra.locator.SimpleSeedProvider
      parameters:
          # You can use any node addresses of your cluster as seeds
          # Ex: "<ip1>,<ip2>,<ip3>"
          # Here we use xcnc35.comp.nus.edu.sg and xcnc36.comp.nus.edu.sg as seeds
          - seeds: "192.168.48.184,192.168.48.185"
```
Set listen address
```yaml
listen_address:  # Leave it blank
```
Set request timeout
```yaml
# Use larger timeouts to handle aggregate queries on database state
read_request_timeout_in_ms: 500000
range_request_timeout_in_ms: 1000000
write_request_timeout_in_ms: 200000
request_timeout_in_ms: 1000000
```

### Run Cassandra
Since Cassandra is assumed to be in the PATH, simply executing `cassandra` in the terminal will let Cassandra run in the background.

### Install Python modules
You should install these modules of Python in advance:
1. cassandra-driver
2. numpy
3. pandas

## Conducting experiments

We assume our project's root directory of Cassandra is `/cassandra-root/`. So for the `src` directory of the project (Cassandra), we will denote it by `/cassandra-root/src`.

For the data files and transaction files in the given `project-files.zip`, we assume they have been downloaded to `/cassandra-root/project-files/data-files/` and `/cassandra-root/project-files/xact-files/` respectively.

### Database preprocessing
Run CQLSH
```bash
cqlsh
```
Create tables and import CSV files
```bash
source '/cassandra-root/src/setup.cql'
```
_Preprocess tables (for experiment 1 & 3)_
```bash
python3 /cassandra-root/src/main.py QUORUM preprocess
```
_Preprocess tables (for experiment 2 & 4)_
```bash
python3 /cassandra-root/src/main.py ROWA preprocess
```
Start experiment on each node simultaneously
(For experiment _i_ and node _j_)
```bash
sh /cassandra-root/experiments/node<j>/ex<i>.sh
```
Check the states of each client  (running or terminated)
(For experiment _i_)
```bash
wc -l exp<i>*
```
Retrieve database state
(For experiment _i_)
```bash
python3 /cassandra-root/src/stats/db_state.py <i>
```

### Postprocessing
Merge runtime statistics of each client
```bash
sh /cassandra-root/experiments/cat_all.sh
```
Merge throughput statistics of each experiment
```bash
python3 /cassandra-root/src/stats/throughputs.py /cassandra-root/project-files/output-files/final_result.csv
```
Merge database states
```bash
# TODO: not implemented
```

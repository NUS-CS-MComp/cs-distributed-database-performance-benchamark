# Cassandra

## Getting Started

We assume Cassandra is already installed on each node, and is included in the PATH environment variable.

### Configure `cassandra.yaml`
Set cluster name:
```yaml
cluster_name: 'CS5424 GrpO'
```
Set addresses of bootstrapping points:
```yaml
seed_provider:
    - class_name: org.apache.cassandra.locator.SimpleSeedProvider
      parameters:
          # You can use any node addresses of your cluster as seeds
          # Ex: "<ip1>,<ip2>,<ip3>"
          # Here we use xcnc35.comp.nus.edu.sg and xcnc36.comp.nus.edu.sg as seeds
          - seeds: "192.168.48.184,192.168.48.185"
```
Set listen address:
```yaml
listen_address:  # Leave it blank
```
Set request timeout:
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
Run CQLSH:
```bash
cqlsh
```
Create tables and import CSV files:
```bash
source '/cassandra-root/src/setup.cql'
```
_Preprocess tables (for experiment 1 & 3):_
```bash
python3 /cassandra-root/src/main.py QUORUM preprocess
```
_Preprocess tables (for experiment 2 & 4):_
```bash
python3 /cassandra-root/src/main.py ROWA preprocess
```
Preprocessing the tables takes approximately 1.5 hours.
It's better to export the preprocessed table so that they can be easily imported next time.
We provided two cql scripts, namely export_preprocessed.cql and import_preprocessed.cql for this purpose.
Note that the cql script does not support CLI arguments, so the user needs to customize the source/destination directory in the script themselves.
Execute the following in cqlsh:
```bash
source '/cassandra-root/src/export_preprocessed.cql
source '/cassandra-root/src/import_preprocessed.cql
```
Start experiment on each node simultaneously
(For experiment _i_ and node _j_, path to main.py script _s_, path to directory with xact test files _x_, path to output directory _o_):
```bash
s=
x=
o=
sh /cassandra-root/experiments/node<j>/ex<i>.sh s x o
```
Check the states of each client  (running or terminated)
(For experiment _i_):
```bash
wc -l exp<i>*
```
Retrieve database state
(For experiment _i_):
```bash
python3 /cassandra-root/src/stats/db_state.py <i>
```

### Postprocessing
Merge runtime statistics of each client
(Given _output_ which is the path to the output directory where all the metric files reside in):
```bash
output=
sh /cassandra-root/experiments/cat_all.sh output
```
Merge throughput statistics of each experiment:
```bash
python3 /cassandra-root/src/stats/throughputs.py /cassandra-root/project-files/output-files/clients.csv
```
Merge database states:
```bash
sh /cassandra-root/src/stats/cat_db_state.sh
```

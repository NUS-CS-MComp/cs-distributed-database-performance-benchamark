# CockroachDB

This path contains all necessary dependencies and source codes to bootstrap distributed database system experiments.

## Project Structure

```bash
.
├── README.md
├── __init__.py
├── client  # Client handler folder
├── modules  # Core modules including model, transaction class and connection configuration
└── scripts  # Bash scripts for infrastructure
```

## Prerequisites

- SSH key to server clusters established via `ssh-copy-id` or manually under `~/.ssh/authorized_keys`

## Getting Started

First, under `scripts/` folder, install CockroachDB binary on your local machine:

```bash
cd scripts
curl https://binaries.cockroachdb.com/cockroach-v19.2.10.darwin-10.9-amd64.tgz | tar -xJ
mv cockroach-v19.2.10.darwin-10.9-amd64.tgz/ bin/  # Renaming
alias cockroach="./bin/cockroach"  # Recommended
```

Next, for deployment to production, go to the corresponding folder:

```bash
cd scripts/prod
```

a CLI tool is ready for use under `scripts/prod/bootstrap.sh`:

```bash
> bash bootstrap.sh -u
Usage: bootstrap.sh [-u] [-q] [-l hosts] [-n <number>] [-k <string>] [-t <string>] [-f <string>] [-p <number>] [-h <number>]
  -u check usage
  -l list of hosts
  -n number of nodes to initiate
  -k ssh key path
  -t client key user name
  -f folder name to store related data
  -p default db port
  -h default http port
  -q flag to shutdown existing instances
```

For your convenience, you can change the default configuration under `scripts/prod/default.sh`:

```bash
> cat default.sh
#!/bin/bash
FOLDER_NAME=/temp/group_o_2020
USER='cs4224o'
NUM_SERVERS=5
SERVER_HOSTS='xcnc35.comp.nus.edu.sg,xcnc36.comp.nus.edu.sg,xcnc37.comp.nus.edu.sg,xcnc38.comp.nus.edu.sg,xcnc39.comp.nus.edu.sg'
PORT=26262
HTTP_PORT=8081
```

Required format for CLI is described as below:
- `-l`: list of hosts separated by comma, e.g. `xcnc35.comp.nus.edu.sg,xcnc36.comp.nus.edu.sg,xcnc37.comp.nus.edu.sg,xcnc38.comp.nus.edu.sg,xcnc39.comp.nus.edu.sg`
- `-n`: number of nodes in integer value; the program will use host list length by default should the numbers not match each other
- `-k`: ssh key path, e.g. `~/.ssh/id_rsa`
- `-t`: user name to be used to create for certificate key and database, e.g. `cs5424o`
- `-f`: folder to store relevant data in the remote server, e.g. `/temp/project_cs5424`
- `-p`: default database port, `26262` by default
- `-h`: default http listening port for the console, `8081` by default
- `-q`: specify this flag if you want to shutdown all instances in the remote server, i.e. `bash bootstrap.sh -q`

Use example:

```bash
bash bootstrap.sh -l host1.com,host2.com,host3.com -n 3 -k ~/.ssh/id_rsa -t cs4224o -f /temp/cockroach -p 26257 -h 8080
```

The message below would suggest that the script was run successfully:

```bash
Cluster successfully initialized
```

## Running Experiments

### Prerequisites

You should have cloned this repository in the remote server and have all the dependencies installed. To reiterate:

- Python 3.8 with dependencies installed on the server as shown in `requirements.txt`/`Pipfile`
    > We use virtual environment to develop this project and `Pipenv` to manage the dependencies; the `requirements.txt` was retrieved via `pipenv run pip freeze` and thus might not be the most updated. We highly encourage you to install `Pipenv` globally and follow the documentation to start this project via `pipenv install` under the directory where `Pipfile` is located. 
- PostgreSQL
    > If you're having trouble installing PostgreSQL globally, e.g. no `root` access, you could change the `psycopg2` dependency in `Pipfile`/`requirements.txt` to `psycopg2-binary` thought it is discouraged to do so under production environment.
- [HIGHLY ENCOURAGED] Pipenv (See [Documentation](https://docs.pipenv.org/basics/))

### Pre-work

Navigate to the top folder:

```bash
cd $WORKSPACE  # Go to the top folder
```

Assuming Python and `Pipenv` is successfully installed on the server, run:

```bash
pipenv install
```

> If you're receiving message containing errors related to `psycopg2`, change the dependency to `psycopg2-binary` in `Pipfile` or `requirements.txt`.

After all dependencies are successfully installed, activate the environment by calling:

```bash
pipenv shell
```

Congratulations! You're now able to run your experiments.

### Procedures

Every time before you start a new experiment, to ensure that the clusters are in clean state, run on your local machine:

```bash
cd cockroachdb/scripts/prod
bash bootstrap.sh
```

The second line could be changed depending on your connection configuration. Navigate to the top of this file to re-familiarize yourself.

Let's go back to the top folder:

```bash
cd $WORKSPACE
```

Another CLI is ready for you to run experiment on the server:

```bash
> python -m cockroachdb.client.main -h
usage: main.py [-h] [--hosts HOSTS] [--port PORT] [-l] [-w WORKERS] [--batch-size BATCH_SIZE] [-e] [--cockroachdb] [-en EXPERIMENT_NUMBER] [-dl LOAD_DATA_PATH]
               [-dt TRANSACTION_DATA_PATH]

optional arguments:
  -h, --help            show this help message and exit
  --hosts HOSTS         List of hosts to resolve
  --port PORT           Database port number
  -l, --load            Load data into database
  -w WORKERS, --workers WORKERS
                        Number of processes to load data
  --batch-size BATCH_SIZE
                        Batch size of loading data
  -e, --experiment      Run experiment
  --cockroachdb         Run experiment in CockroachDB
  -en EXPERIMENT_NUMBER, --experiment-number EXPERIMENT_NUMBER
                        Experiment number
  -dl LOAD_DATA_PATH, --load-data-path LOAD_DATA_PATH
                        Path to read initial data
  -dt TRANSACTION_DATA_PATH, --transaction-data-path TRANSACTION_DATA_PATH
                        Path to read transaction data
```

For your convenience, download the data and unzip it under the top folder, for example:

```bash
➜ ls -ls data/
total 0
0 drwx------@  9 luter  staff   288 Aug 27 22:24 data-files
0 drwxr-xr-x   7 luter  staff   224 Nov  1 21:06 test-xact-files
0 drwx------@ 42 luter  staff  1344 Aug 27 22:24 xact-files
```

For the following steps, we recommend you to run the program in the server as the multiprocessing could drain your local machine pretty fast.

#### Load Initial Data with Specified Worker and Batch Size

```bash
ENV=prod python -m cockroachdb.client.main -l --cockroachdb --workers 16 --batch-size 2999 --ports=26257 \
    --hosts xcnc35.comp.nus.edu.sg,xcnc36.comp.nus.edu.sg,xcnc37.comp.nus.edu.sg,xcnc38.comp.nus.edu.sg,xcnc39.comp.nus.edu.sg
```

> It is important to set `ENV=prod` unless you want to test it locally

### Run Experiment with Specified Experiment Number

```bash
# Run Experiment 5 on CockroachDB
ENV=prod python -m cockroachdb.client.main -e --cockroachdb -en 5 --ports=26257 \
    --hosts xcnc35.comp.nus.edu.sg,xcnc36.comp.nus.edu.sg,xcnc37.comp.nus.edu.sg,xcnc38.comp.nus.edu.sg
```

> Caveat: the values specified should match the one you provide in `bootstrap.sh`

# CockroachDB

- [CockroachDB](#cockroachdb)
  - [Getting Started](#getting-started)
    - [Generate Certificate for Each Node](#generate-certificate-for-each-node)
    - [Install CockroachDB Binary on Remote Servers](#install-cockroachdb-binary-on-remote-servers)
    - [Bootstrap Nodes on Remote Servers](#bootstrap-nodes-on-remote-servers)
    - [Shutdown Nodes](#shutdown-nodes)

## Getting Started

First, go to infrastructure folder and install CockroachDB on local machine:

```bash
cd infrastructure
curl https://binaries.cockroachdb.com/cockroach-v19.2.10.darwin-10.9-amd64.tgz | tar -xJ
mv cockroach-v19.2.10.darwin-10.9-amd64.tgz/ bin/ # renaming
```

### Generate Certificate for Each Node

```bash
source generate-cert.sh
```

### Install CockroachDB Binary on Remote Servers

```bash
source install-db.sh
```

### Bootstrap Nodes on Remote Servers

```bash
source bootstrap.sh
```

### Shutdown Nodes

> WARNING: Shutting down nodes might have unintended effects on stored data.

```bash
source shutdown.sh
```

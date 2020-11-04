#!/bin/bash

mkdir -p certs/ keys/

if [ ! -f certs/ca.crt ]; then
  cockroach cert create-ca --certs-dir=certs --ca-key=keys/ca.key
  cockroach cert create-node localhost "$(hostname)" --certs-dir=certs --ca-key=keys/ca.key
  cockroach cert create-client root --certs-dir=certs --ca-key=keys/ca.key
fi

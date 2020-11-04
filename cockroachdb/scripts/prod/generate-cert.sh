#!/bin/bash

create_certs() {
  host=$1
  user=$2
  if [ ! -f server_certs/"$host"/ca.crt ]; then
    echo "Creating new certificate for host $host"
    cockroach cert create-node localhost "$host" --certs-dir=certs --ca-key=keys/ca.key
    cockroach cert create-client root --certs-dir=certs --ca-key=keys/ca.key
    cockroach cert create-client "$user" --certs-dir=certs --ca-key=keys/ca.key
    mkdir -p server_certs/"$host"/
    cp certs/* server_certs/"$host"/
    rm certs/node.crt certs/node.key certs/client*
  fi
}

upload_certs() {
  host=$1
  user=$2
  key=$3
  folder=$4
  echo "Uploading new certificate to host $user@$host:$folder"
  ssh -i "$key" "$user"@"$host" "mkdir -p $folder/cockroachdb/certs"
  scp server_certs/"$host"/* "$user"@"$1":"$folder"/cockroachdb/certs/
}

#!/bin/bash

create_group_folder() {
  folder=$1
  if [ ! -e "$folder" ]; then
    mkdir "$folder"
  fi
  if [ ! -e "$folder"/cockroachdb ]; then
    mkdir "$folder"/cockroachdb
  fi
}

install_cockroachdb() {
  folder=$1
  if [ ! -e "$folder"/cockroachdb/bin/ ]; then
    cd "$folder"/cockroachdb || exit
    wget -qO- https://binaries.cockroachdb.com/cockroach-v19.2.9.linux-amd64.tgz | tar xvz
    mv cockroach-v19.2.9.linux-amd64/ bin/
  else
    exit 1
  fi
}

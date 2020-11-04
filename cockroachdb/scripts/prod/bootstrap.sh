#!/bin/bash

# Usage example:
# bash bootstrap.sh -l host1.com,host2.com,host3.com -n 3 -k ~/.ssh/id_rsa -t cs4224o -f /temp/cockroach -p 26257 -h 8080

usage() {
  echo "Usage: $0 [-u] [-q] [-l hosts] [-n <number>] [-k <string>] [-t <string>] [-f <string>] [-p <number>] [-h <number>]" 1>&2
  echo "  -u check usage" 1>&2
  echo "  -l list of hosts" 1>&2
  echo "  -n number of nodes to initiate" 1>&2
  echo "  -k ssh key path" 1>&2
  echo "  -t client key user name" 1>&2
  echo "  -f folder name to store related data" 1>&2
  echo "  -p default db port" 1>&2
  echo "  -h default http port" 1>&2
  echo "  -q flag to shutdown existing instances" 1>&2
}

while getopts ":u:n:l:k:t:f:p:h:q" o; do
  case "${o}" in
  l)
    l=${OPTARG}
    ;;
  n)
    n=${OPTARG}
    ;;
  k)
    k=${OPTARG}
    ;;
  t)
    t=${OPTARG}
    ;;
  f)
    f=${OPTARG}
    ;;
  p)
    p=${OPTARG}
    ;;
  h)
    h=${OPTARG}
    ;;
  q)
    SHUTDOWN='true'
    ;;
  *)
    usage
    exit
    ;;
  esac
done
shift $((OPTIND - 1))

source ./default.sh

if [ -z "$l" ]; then
  l="${SERVER_HOSTS[*]}"
fi

if [ -z "$n" ]; then
  n=$NUM_SERVERS
fi

if [ -z "$k" ]; then
  k=$HOME/.ssh/id_rsa
fi

if [ -z "$t" ]; then
  t="$USER"
fi

if [ -z "$f" ]; then
  f="$FOLDER_NAME"
fi

if [ -z "$p" ]; then
  p="$PORT"
fi

if [ -z "$h" ]; then
  h="$HTTP_PORT"
fi

split_list() {
  hosts=()
  host_list=()
  http_list=()
  host_ports=()
  http_ports=()
  if [[ ! $l =~ .+,.+ ]]; then
    echo "Same host address detected. Increment HTTP listening port by 1 for each node."
    hosts+=("$l")
    for inc in $(seq 1 "$n"); do
      host_list+=("$l:$((p + inc - 1))")
      http_list+=("$l:$((h + inc - 1))")
      host_ports+=($((p + inc - 1)))
      http_ports+=($((h + inc - 1)))
    done
  else
    local IFS=','
    for host in $l; do
      hosts+=("$host")
      if [[ $host =~ .+:.+ ]]; then
        host_list+=("$host")
      else
        host_list+=("$host":"$p")
      fi
      http_list+=("$host":"$h")
      host_ports+=("$p")
      http_ports+=("$h")
    done
  fi
}

split_list
if [ ${#host_list[@]} -ne "$n" ]; then
  echo "Host list length does not equal number of servers provided ($n). Use length (${#host_list[*]}) of [${host_list[*]}] instead."
fi

start_instances() {
  current_server=$1
  current_node=$2
  current_node_http=$3
  node_port=$4
  timestamp=$6
  node_addresses=()
  local index
  for ((index = 0; index < ${#host_list[@]}; ++index)); do
    host=${host_list[$index]}
    if [ "$host" != "$current_node" ]; then
      node_addresses+=("$host")
    fi
  done
  join_address=$(printf ",%s" "${node_addresses[@]}")
  join_address=${join_address:1}
  ssh -i "$k" "$t"@"$current_server" "source ~/.bash_profile; cockroach start --certs-dir=$f/cockroachdb/certs --store=$f/cockroachdb/store/$timestamp/node_$node_port --listen-addr=$current_node \
    --http-addr=$current_node_http --join=$join_address --background > /dev/null 2>&1 &"
}

kill_existing_process() {
  server=$1
  folder=$2
  echo "Terminating existing Cockroach instances..."
  # rm -rf "$folder"/cockroachdb/store
  for pid in $(ps -ef | grep -v grep | grep "cockroach" | awk '{print $2}'); do kill -9 "$pid"; done
  local index
  http_port=${http_ports[$index]}
  http_process=$(ps -ef | grep -v grep | grep "$server:$http_port" | awk '{print $2}')
  if [ -n "$http_process" ]; then
    echo "Killing existing processes at HTTP port $http_port..."
    kill -9 "$http_process"
  fi
}

kill_and_start() {
  local epoch
  epoch=$(date +%s)
  for ((index = 0; index < ${#host_list[@]}; ++index)); do
    server=${hosts[$index]}
    # shellcheck disable=SC2034
    ssh -i "$k" "$t"@"$server" "$(typeset -f kill_existing_process); kill_existing_process $server $f"
    echo "Starting node with host ${host_list[$index]}..."
    start_instances "$server" "${host_list[$index]}" "${http_list[$index]}" "${host_ports[$index]}" "${http_ports[$index]}" "$epoch"
  done
}

if [ $SHUTDOWN == 'true' ]; then
  for ((index = 0; index < ${#host_list[@]}; ++index)); do
    server=${hosts[$index]}
    # shellcheck disable=SC2034
    ssh -i "$k" "$t"@"$server" "$(typeset -f kill_existing_process); kill_existing_process $server $f"
  done
  exit
fi

# Install database

source ./install-db.sh

for server in "${hosts[@]}"; do
  echo "Installing Cockroach DB on server $server"
  # shellcheck disable=SC2034
  ssh -i "$k" "$t"@"$server" "$(typeset -f create_group_folder); $(typeset -f install_cockroachdb); create_group_folder $f && install_cockroachdb $f && echo 'export PATH=$f/cockroachdb/bin:\$PATH' >> ~/.bash_profile"
done

# Generate certificates

source ./generate-cert.sh

if [ ! -f certs/ca.crt ]; then
  mkdir -p certs/ keys/
  cockroach cert create-ca --certs-dir=certs --ca-key=keys/ca.key --allow-ca-key-reuse
fi

for server in "${hosts[@]}"; do
  create_certs "$server" "$t" && upload_certs "$server" "$t" "$k" "$f"
done

# Bootstrapping new database instances

kill_and_start &&
  cockroach init --certs-dir=server_certs/"${hosts[0]}" --host="${host_list[0]}" &&
  cockroach sql --certs-dir=server_certs/"${hosts[0]}" --host="${host_list[0]}" --port="${host_ports[0]}" <"../db/init_db_schema.sql"

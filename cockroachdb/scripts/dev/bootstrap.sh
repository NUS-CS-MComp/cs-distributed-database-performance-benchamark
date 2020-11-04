#!/bin/bash

usage() {
  echo "Usage: $0 [-u] [-n <number>] [-l hosts] [-p <number>] [-h <number>]" 1>&2
  echo "  -u check usage" 1>&2
  echo "  -n number of nodes to initiate" 1>&2
  echo "  -l list of hosts" 1>&2
  echo "  -p default db port" 1>&2
  echo "  -h default http port" 1>&2
}

while getopts ":u:n:l:p:h" o; do
  case "${o}" in
  n)
    n=${OPTARG}
    ;;
  l)
    l=${OPTARG}
    ;;
  p)
    p=${OPTARG}
    ;;
  h)
    h=${OPTARG}
    ;;
  *)
    usage
    exit
    ;;
  esac
done
shift $((OPTIND - 1))

if [ -z "$n" ]; then
  n=5
fi

if [ -z "$l" ]; then
  l=localhost
fi

if [ -z "$p" ]; then
  p=26257
fi

if [ -z "$h" ]; then
  h=8080
fi

if [[ ! $l =~ .+,.+ ]]; then
  if [[ $l =~ .+:.+ ]] && [[ n -gt 1 ]]; then
    echo "Invalid host provided with number of nodes = $n."
    exit 1
  fi
fi

split_list() {
  host_list=()
  http_list=()
  host_ports=()
  http_ports=()
  if [[ ! $l =~ .+,.+ ]]; then
    echo "Same host address detected. Increment HTTP listening port by 1 for each node."
    for inc in $(seq 1 $n); do
      host_list+=("$l:$((p + inc - 1))")
      http_list+=("$l:$((h + inc - 1))")
      host_ports+=($((p + inc - 1)))
      http_ports+=($((h + inc - 1)))
    done
  else
    local IFS=','
    for host in $l; do
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
if [ ${#host_list[@]} -ne $n ]; then
  echo "Host list length does not equal number of servers provided. Use length ${#host_list[*]} of [${host_list[*]}] instead."
fi

start_instances() {
  current_node=$1
  current_node_http=$2
  node_port=$3
  timestamp=$5
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
  cockroach start --certs-dir=certs --store=store/"$timestamp"/node_"$node_port" --listen-addr="$current_node" \
    --http-addr="$current_node_http" --join="$join_address" --background
}

kill_and_start() {
  echo "Clearing existing Cockroach instances and removing all data..."
  for pid in $(ps -ef | grep -v grep | grep "cockroach" | awk '{print $2}'); do kill -9 "$pid"; done
  rm -rf node_*/
  local index
  local epoch
  epoch=$(date +%s)
  for ((index = 0; index < ${#host_list[@]}; ++index)); do
    http_port=${http_ports[$index]}
    http_process=$(lsof -t -i:"$http_port")
    if [ -n "$http_process" ]; then
      echo "Killing existing processes at HTTP port $http_port..."
      kill -9 "$http_process"
    fi
    echo "Starting node with host $host..."
    start_instances "${host_list[$index]}" "${http_list[$index]}" "${host_ports[$index]}" "${http_ports[$index]}" "$epoch"
  done
}

kill_and_start &&
  cockroach init --certs-dir=certs --host="${host_list[0]}" &&
  cockroach sql --certs-dir=certs --host="${host_list[0]}" --port="${host_ports[0]}" <"../db/init_db_schema.sql"

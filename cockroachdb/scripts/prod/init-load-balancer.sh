#!/bin/zsh

# DEPRECATED

source ./config.sh

cockroach gen haproxy --certs-dir=certs_$LOADER_BALANCER_SERVER --host=xcnc$LOADER_BALANCER_SERVER.comp.nus.edu.sg:$PORT

function install_haproxy {
  if [ ! -e $FOLDER_NAME/cockroachdb/bin/haproxy ]; then
    cd $FOLDER_NAME/cockroachdb
    wget -qO- https://www.haproxy.org/download/2.2/src/haproxy-2.2.4.tar.gz | tar xvz
    mv haproxy-2.2.4/ haproxy/
    cd haproxy/
    make TARGET=linux-glibc && mv ./haproxy ../bin/
  fi
}

ssh $USER@xcnc$LOADER_BALANCER_SERVER.comp.nus.edu.sg "$(typeset -f install_haproxy); FOLDER_NAME=$FOLDER_NAME; install_haproxy";
scp ./haproxy.cfg $USER@xcnc$LOADER_BALANCER_SERVER.comp.nus.edu.sg:$FOLDER_NAME/cockroachdb/
ssh $USER@xcnc$LOADER_BALANCER_SERVER.comp.nus.edu.sg "FOLDER_NAME=$FOLDER_NAME; cd $FOLDER_NAME/cockroachdb; bin/haproxy -f haproxy.cfg &";

#!/bin/zsh

source ./config.sh

cockroach node decommission $(($SERVER_SEQ_END-$SERVER_SEQ_START+1))\
 --certs-dir=certs_$SERVER_SEQ_END --host=xcnc$SERVER_SEQ_START.comp.nus.edu.sg:$PORT # Decommission last node

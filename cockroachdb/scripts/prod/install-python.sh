#!/bin/zsh

source ./config.sh

export LD_LIBRARY_PATH=$FOLDER_NAME/libffi33/lib64
export LD_RUN_PATH=$FOLDER_NAME/libffi33/lib64
CPPFLAGS=-I$FOLDER_NAME/libffi-3.3/include LDFLAGS=-L$FOLDER_NAME/libffi33/lib64 ./configure --prefix=$FOLDER_NAME/python38

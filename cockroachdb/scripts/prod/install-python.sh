#!/bin/zsh

export LD_LIBRARY_PATH=/temp/group_o_2020/libffi33/lib64
export LD_RUN_PATH=/temp/group_o_2020/libffi33/lib64
CPPFLAGS=-I/temp/group_o_2020/libffi-3.3/include LDFLAGS=-L/temp/group_o_2020/libffi33/lib64 ./configure --prefix=/temp/group_o_2020/python38

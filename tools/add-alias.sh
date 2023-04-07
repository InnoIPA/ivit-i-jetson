#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"
ROOT=`realpath "${DIR}/../"`

echo "alias run-ivit-i='cd ${ROOT} && ./docker/run.sh -qnb'" >> ~/.bashrc
echo "alias stop-ivit-i='cd ${ROOT} && ./docker/stop.sh'" >> ~/.bashrc
source ~/.bashrc
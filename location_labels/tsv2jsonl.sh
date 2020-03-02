#!/bin/bash
SCRIPT_NAME=$(basename $BASH_SOURCE) 

if [ $# -eq 0 ]
  then
    echo "No arguments supplied."
    echo "usage: ${SCRIPT_NAME} [labels.tsv file]"
    exit
fi

cat $1 | jq -c --raw-input --raw-output 'split("\n") | map(split("\t"))  | map( {"location_uri": .[0], "label": .[1]}) | .[0]' | sed 's/\\r//g' 


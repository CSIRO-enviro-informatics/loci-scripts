#!/bin/bash

INDEX_NAME=default_index

echo 'uncompressing location_labels.tar.gz'
FILE=location_labels.tar.gz
if [ -f "$FILE" ]; then
    echo "$FILE exist"
    echo "uncompressing $FILE ..."
    tar zxvf location_labels.tar.gz
else 
    echo "$FILE does not exist... check if location_labels.tsv exists"
fi

FILE=location_labels.tsv
if [ ! -f "$FILE" ]; then
    echo "$FILE does not exist"
    exit
fi

#assumes location_labels.tsv file exists
echo 'splitting tsv and converting to es json'
split -dl 100000 --additional-suffix=.tsv location_labels.tsv split-loc-labels-

ls split-loc-labels-*.tsv | xargs -i echo "cat '{}' | jq -c --raw-input --raw-output 'split(\"\\n\") | map(split(\"\\t\"))  | map( {\"location_uri\": .[0], \"label\": .[1]}) | .[0]' | sed 's/\\\\r//g' | jq -c '. | {\"index\" :{ \"_index\" : \"$INDEX_NAME\", \"_type\" : \"location\", }}, {\"uri\": .location_uri, \"label\": .label}' > ./{}.json" | bash


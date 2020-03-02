#!/bin/bash

ls *.json | xargs -i curl -s -XPOST -H "Content-Type: application/json" http://localhost:9200/_bulk --data-binary @{}

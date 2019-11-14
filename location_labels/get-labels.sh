#!/bin/bash
DATE=`date "+%Y%m%d"`

python -m pyloci.sparql.query_loci_location_labels --limit 100000000 > location_labels_${DATE}.tsv

#then run  tsv2jsonl.sh

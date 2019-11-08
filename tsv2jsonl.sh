
cat location_labels2.tsv | jq -c --raw-input --raw-output 'split("\n") | map(split("\t"))  | map( {"location_uri": .[0], "label": .[1]}) | .[0]' | sed 's/\\r//g' > location_labels.jsonl


Run the following to get the location_labels es dataset

```
$ ./get-labels.sh
$ tar cvvzf location_labels.tar.gz location_labels.tsv 
$ sha256sum location_labels.tar.gz > location_labels.tar.gz.sha256
$ ./preprocess.sh
$ tar cvvzf loc-labels-es-json.tar.gz split-loc-labels*.tsv.json
$ sha256sum loc-labels-es-json.tar.gz > loc-labels-es-json.tar.gz.sha256
```

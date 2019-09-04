#!/bin/bash

python -m pyloci.sparql.generate_loci_uri_to_id_mappings

for i in asgs2016-*.csv; do
    zip ${i}.zip ${i}
    md5sum ${i}.zip > ${i}.zip.md5
done
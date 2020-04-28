# LOC-I SCRIPTS and pyloci

[![Build Status](https://travis-ci.org/CSIRO-enviro-informatics/loci-scripts.svg?branch=master)](https://travis-ci.org/CSIRO-enviro-informatics/loci-scripts)

### A collection of scripts, snippets, and mini-apps from the LOC-I Project

### .env

Copy the env-template to .env and edit the file to specify which sparql endpoint
and authentication details if needed

### Setup

```
$ pip install -e .
```

For tests involving selenium, `chromedriver` is required.
```
# Install on windows
$ choco install chromedriver

# Install on linux
# See https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/
```

Example uses
```
# Run stats over the loci dataset
$ python -m pyloci.sparql.generate_loci_type_count 

# query contains for a precanned set of uris
$ python -m pyloci.sparql.query_loci_mb16cc_contains

# query contains for a precanned set of uris
$ python -m pyloci.sparql.query_loci_mb16cc_contains '<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12101547>'
```
### Reapportioning use case

```
# reapportion single-cc-mb16-within.csv in verbose mode with output to specific csv file
$ python -m pyloci.reapportioning --verbose -o output.csv ./loci-testdata/excelerator/single-cc-mb16-within.csv

# reapportion single-cc-mb16-within.csv in verbose mode with output to stdout
$ python -m pyloci.reapportioning --verbose ./loci-testdata/excelerator/single-cc-mb16-within.csv

# reapportion single-cc-mb16-within.csv in non-verbose mode with output to stdout
$ python -m pyloci.reapportioning ./loci-testdata/excelerator/single-cc-mb16-within.csv

# reapportion single-cc-mb16-within.csv in non-verbose mode with output to specific csv file
$ python -m pyloci.reapportioning -o output.csv ./loci-testdata/excelerator/single-cc-mb16-within.csv

# process all .csv files in input dir ('-d' specifies process directory mode)
$ python -m pyloci.reapportioning -d  ./loci-testdata/excelerator
```

### Generate Test Data
```
# Run stats over the loci dataset
$ python -m pyloci.sparql.generate_loci_type_count > ./loci-testdata/loci_type_count.json

# Create test_case_contains_result testdata
$ python -m pyloci.sparql.generate_loci_contains_testdata > ./loci-testdata/test_case_contains_result.json

# Create reapportioning test dataset - queries contains for Test Case A-C set of URIs 
$ python -m pyloci.sparql.generate_loci_reapportioning_testdata > ./loci-testdata/loci_reapportioning_testdata.json


# Create loci mb16cc relations test data - query mb and cc relationships (without specifying the predicate) - currently broken :(
$ python -m pyloci.sparql.generate_loci_mb16cc_relations_testdata > ./loci-testdata/test_case_mb16cc_relations_result.json

# query labels
$ python -m pyloci.sparql.query_loci_location_labels --limit 100 --max 100 > location_labels.tsv

# generate loci test LD dataset
$ python -m pyloci.generate_loci_rdf_testdata

```

### Running tests
```
$ pytest
```


## Rights & License
The content of this repository is &copy; 2019 CSIRO Land and Water.  
The content of this repository is distributed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0)

## Contacts

**Ashley Sommer**  
*Informatics Software Engineer*  
CSIRO Land & Water, Environmental Informatics Group  
<ashley.sommer@csiro.au>  
<https://orcid.org/0000-0003-0590-0131>  


**Benjamin Leighton**  
*Informatics Software Engineer*  
CSIRO Land & Water, Environmental Informatics Group  

**Jonathan Yu**  
*Data scientist*  
CSIRO Land & Water, Environmental Informatics Group  


**Nicholas Car**  
*Senior Experimental Scientist*  
CSIRO Land & Water, Environmental Informatics Group  
<nicholas.car@csiro.au>  
<http://orcid.org/0000-0002-8742-7730>  


# LOC-I SCRIPTS and pyloci

### A collection of scripts, snippets, and mini-apps from the LOC-I Project

### .env

Copy the env-template to .env and edit the file to specify which sparql endpoint
and authentication details if needed

### Setup

```
$ pip install -e .
```

Example uses
```
# Run stats over the loci dataset
$ python -m pyloci.sparql.generate_loci_type_count 
```

### Generate Test Data
```
# Run stats over the loci dataset
$ python -m pyloci.sparql.generate_loci_type_count > ./loci-testdata/loci_type_count.json

# Create loci_withins_test_data
$ python -m pyloci.sparql.generate_loci_withins_testdata > ./loci-testdata/test_case_withins_result.json

# Create loci
$ python -m pyloci.sparql.generate_loci_mb16cc_relations_testdata > ./loci-testdata/test_case_mb16cc_relations_result.json
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


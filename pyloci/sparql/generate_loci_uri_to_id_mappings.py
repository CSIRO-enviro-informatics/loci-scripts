from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from . import util

GRAPHDB_USER = os.getenv("GRAPHDB_USER")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")

def main():
    # uncomment the following GRAPHDB_SPARQL and auth variables for test repo
    #GRAPHDB_SPARQL = GRAPHDB_SPARQL_TEST
    auth = None
    # set auth only if .env has credentials
    if(GRAPHDB_USER != None and GRAPHDB_PASSWORD != None):
        auth = { 
            "user" : GRAPHDB_USER,
            "password" : GRAPHDB_PASSWORD   
        }

    loci_types = [    
        ["asgs2016-sa4","<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel4>", "<http://linked.data.gov.au/def/asgs#sa4Code2016>"],
        ["asgs2016-sa3","<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel3>", "<http://linked.data.gov.au/def/asgs#sa3Code2016>"],
        ["asgs2016-sa2","<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel2>", "<http://linked.data.gov.au/def/asgs#sa2Maincode2016>"],
        ["asgs2016-sa1", "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1>", "<http://linked.data.gov.au/def/asgs#sa1Maincode2016>"],       
        ["asgs2016-mb", "<http://linked.data.gov.au/def/asgs#MeshBlock>", "<http://linked.data.gov.au/def/asgs#mbCode2016>"]
    ]

    count_types = []
    for curr in loci_types:
        l = util.query_uri_id_mapping_table(curr[1], curr[2], SPARQL_ENDPOINT, auth=auth)
        writeListToCsvFile(l, curr[0]+"_uris.csv")

import csv 
def writeListToCsvFile(l, fname):
    print("Writing to " + fname + "...")
    with open(fname, 'w', newline='') as csvfile:
        w = csv.writer(csvfile)        
        w.writerow(['id','lociUri'])
        w.writerows(l)


if __name__ == "__main__":
    main()


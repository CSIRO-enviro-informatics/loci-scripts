from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from . import util

    

GRAPHDB_USER = os.getenv("GRAPHDB_USER")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")

# uncomment the following GRAPHDB_SPARQL and auth variables for test repo
#GRAPHDB_SPARQL = GRAPHDB_SPARQL_TEST
auth = None
# set auth only if .env has credentials
if(GRAPHDB_USER != None and GRAPHDB_PASSWORD != None):
    auth = { 
        "user" : GRAPHDB_USER,
        "password" : GRAPHDB_PASSWORD   
    }

loci_thing_list = [
    ["test-case-A-VIC", "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12101547>"],
    ["test-case-A-QLD", "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12202179>"],
    ["test-case-B-ACT", "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80044260000>"],
    ["test-case-B-NT", "<http://linked.data.gov.au/dataset/asgs2016/meshblock/70033750000>"],
    ["test-case-B-QLD", "<http://linked.data.gov.au/dataset/asgs2016/meshblock/30562872900>"],
    ["test-case-B-VIC", "<http://linked.data.gov.au/dataset/asgs2016/meshblock/20686780000>"],
    ["test-case-C-ACT-1", "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12104853>"],
    ["test-case-C-ACT-2", "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105135>"],
    ["test-case-C-ACT-3", "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105134>"]
]

#query()
matches = []
for testcase,currUri in loci_thing_list:
    res = util.query_mb16cc_contains(currUri, SPARQL_ENDPOINT, auth=auth)
    matches.append({"testcase": testcase, "fromUri" : currUri, "matches": res})
    
print(json.dumps(matches, indent=4, sort_keys=False))

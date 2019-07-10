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
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008420000>",
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008441000>",
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008442000>",
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008450000>",
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008460000>",
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008470000>",
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008490000>",
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008500000>",
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008511000>",
    "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008530000>"
]

#query()
print(auth)
matches = []
for curr in loci_thing_list:
    res = util.query_sfWithin(curr, SPARQL_ENDPOINT, auth=auth)
    matches.append({"id" : curr, "matches": res})

print(json.dumps(matches, indent=4, sort_keys=True))

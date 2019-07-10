from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
import sys
import re
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from . import util

GRAPHDB_USER = os.getenv("GRAPHDB_USER")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")


def run_query(curr, sparql_endpoint, auth):
    print("Querying contained areas for " + curr)
    res = util.query_mb16cc_contains(curr, sparql_endpoint, auth=auth)
    sum = 0.0
    fromArea = 0.0
    for d in res:
        sum = float(sum) + float(d['toArea'])
        fromArea = float(d['fromArea'])
    print("sum toArea: " + str(sum))
    print("fromArea: " + str(fromArea))
    print("diff: " + str(fromArea-sum) + "\n")

def validate_uri_syntax(input_str):
    return bool(re.match(r"<http://.+>", input_str))

auth = None
# set auth only if .env has credentials
if(GRAPHDB_USER != None and GRAPHDB_PASSWORD != None):
    auth = { 
        "user" : GRAPHDB_USER,
        "password" : GRAPHDB_PASSWORD   
    }

loci_thing_list = [
    "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12101547>",
    "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12202179>",
    "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12104853>",
    "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105135>"
]

if len(sys.argv) > 1:
    user_input_uri = sys.argv[1]
else:
    user_input_uri = None

matches = []

if user_input_uri != None :
    if validate_uri_syntax(user_input_uri):
        run_query(user_input_uri, SPARQL_ENDPOINT, auth)
    else:
        print("Please provide a valid URI in the form <http://...>")
else:
    for curr in loci_thing_list:
        run_query(curr, SPARQL_ENDPOINT, auth)


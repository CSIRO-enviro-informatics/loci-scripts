"""Loc-I mb16cc linkset contains relation query engine

Provide queries to Loc-I cache for the geo:sfContains relation for 
input URI
"""
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


def query_contains_for_stats(curr, sparql_endpoint, auth):
    """Runs the geo:sfContains relation query
     Parameters
    ----------
    curr : str
        Current uri
    sparql_endpoint : str
        Sparql endpoint
    auth : object
    """
    print("Querying contained areas for " + curr)
    res = util.query_mb16cc_contains(curr, sparql_endpoint, auth=auth)
    sum = 0.0
    fromArea = 0.0
    #print(json.dumps(res, indent=4))
    for d in res:
        if 'toAreaLinkset' in d and d['toAreaLinkset'] != None:
            sum = float(sum) + float(d['toAreaLinkset'])
        elif 'toAreaDataset' in d and d['toAreaDataset'] != None:
            sum = float(sum) + float(d['toAreaDataset'])

        if 'fromAreaLinkset' in d and d['fromAreaLinkset'] != None:
           fromArea = float(d['fromAreaLinkset'])
        elif 'fromAreaDataset' in d and d['fromAreaDataset'] != None:
           fromArea = float(d['fromAreaDataset'])
    
    diff = fromArea-sum
    percentDiffFromArea = 100.0
    if fromArea > 0.0:
        percentDiffFromArea = (diff/fromArea)*100.0

    return (fromArea, sum, diff, percentDiffFromArea)


def print_report(fromArea, sum, diff, percentDiffFromArea):
    line = '{:>15} {:>20.4f}\n{:>15} {:>20.4f}\n{:>15} {:>20.4f}\n{:>15} {:>20.4f}\n'.format(
    "fromArea:", fromArea, 
    "sum toArea:", sum, 
    "diff:", fromArea-sum,
    "% of fromArea:", percentDiffFromArea
    )
    print(line)

if __name__ == "__main__":
    auth = None
    # set auth only if .env has credentials
    if(GRAPHDB_USER != None and GRAPHDB_PASSWORD != None):
        auth = { 
            "user" : GRAPHDB_USER,
            "password" : GRAPHDB_PASSWORD   
        }

    #use this precanned list if there is no user input via sys.argv[1]
    loci_thing_list = [
        "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12101547>",
        "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12202179>",
        "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80044260000>",
        "<http://linked.data.gov.au/dataset/asgs2016/meshblock/70033750000>",
        "<http://linked.data.gov.au/dataset/asgs2016/meshblock/30562872900>",
        "<http://linked.data.gov.au/dataset/asgs2016/meshblock/20686780000>",
        "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12104853>",
        "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105135>",
        "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105134>"    
    ]

    if len(sys.argv) > 1:
        user_input_uri = sys.argv[1]
    else:
        user_input_uri = None

    matches = []

    if user_input_uri != None :
        if util.validate_uri_syntax(user_input_uri):
            (fromArea, sum, diff, percentDiffFromArea) = query_contains_for_stats(user_input_uri, SPARQL_ENDPOINT, auth)
            print_report(fromArea, sum, diff, percentDiffFromArea)
        else:
            print("Please provide a valid URI in the form <http://...>")
            exit(1)
    else:
        for curr in loci_thing_list:
            (fromArea, sum, diff, percentDiffFromArea) = query_contains_for_stats(curr, SPARQL_ENDPOINT, auth)
            print_report(fromArea, sum, diff, percentDiffFromArea)


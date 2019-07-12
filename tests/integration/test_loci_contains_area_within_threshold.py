import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv, find_dotenv
import json

load_dotenv(find_dotenv())

from pyloci.sparql import util, query_loci_mb16cc_contains


GRAPHDB_USER = os.getenv("GRAPHDB_USER")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")


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
    

@pytest.mark.parametrize("region_uri", loci_thing_list)
def test_loci_contains_for_region_is_within_threshold(region_uri):
    auth = None
    # set auth only if .env has credentials
    if(GRAPHDB_USER != None and GRAPHDB_PASSWORD != None):
        auth = { 
            "user" : GRAPHDB_USER,
            "password" : GRAPHDB_PASSWORD   
        }
        
    THRESHOLD = 3.0 #set threshold to 2%
    (fromArea, sum, diff, percentDiffFromArea) = query_loci_mb16cc_contains.query_contains_for_stats(region_uri, SPARQL_ENDPOINT, auth)

    assert percentDiffFromArea <= THRESHOLD

    
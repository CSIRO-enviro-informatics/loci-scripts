import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from pyloci.sparql import util


testdata = [
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008420000>",
        "matches": [
            "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105140"
        ]
    },
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008441000>",
        "matches": [
            "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105140"
        ]
    },
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008442000>",
        "matches": [
            "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105140"
        ]
    },
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008450000>",
        "matches": [
            "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105140"
        ]
    },
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008460000>",
        "matches": [
            "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105140"
        ]
    },
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008470000>",
        "matches": [
            "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105140"
        ]
    },
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008490000>",
        "matches": []
    },
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008500000>",
        "matches": []
    },
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008511000>",
        "matches": [
            "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105140"
        ]
    },
    {
        "id": "<http://linked.data.gov.au/dataset/asgs2016/meshblock/80008530000>",
        "matches": [
            "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105140"
        ]
    }
]

@pytest.mark.parametrize("obj", testdata)
def test_loci_relations(obj):
    '''Test 
    '''
    GRAPHDB_USER = os.getenv("GRAPHDB_USER")
    GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
    SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")
    auth = None
    # set auth only if .env has credentials
    if(GRAPHDB_USER != None and GRAPHDB_PASSWORD != None):
        auth = { 
            "user" : GRAPHDB_USER,
            "password" : GRAPHDB_PASSWORD   
        }

    matches = util.query_sfWithin(obj['id'], SPARQL_ENDPOINT, auth=auth)
    print(matches)
    print(obj["matches"])

    assert all([a == b for a, b in zip(matches, obj['matches'])])

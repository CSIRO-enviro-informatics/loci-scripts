import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from pyloci.sparql import util


def get_verification_data():
    data = {}
    with open('./loci-testdata/loci_type_count.json') as json_file:  
        data = json.load(json_file)        
    return data



@pytest.mark.parametrize("loci_type,count", get_verification_data())
def test_loci_type_counts(loci_type, count):
    '''Test loci type counts
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

    currcount = util.count_type(loci_type, SPARQL_ENDPOINT, auth=auth)
    assert count == currcount
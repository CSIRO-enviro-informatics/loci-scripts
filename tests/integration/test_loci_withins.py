import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv, find_dotenv
import json

load_dotenv(find_dotenv())

from pyloci.sparql import util


def get_verification_data():
    data = {}
    with open('./loci-testdata/test_case_withins_result.json') as json_file:  
        data = json.load(json_file)        
    return data

@pytest.mark.parametrize("verification_data", get_verification_data())
def test_file(verification_data):
    for test_case in verification_data:
        print(test_case)
    assert True

def loci_relations(obj):
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

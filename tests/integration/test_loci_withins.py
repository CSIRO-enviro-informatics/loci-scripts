import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv, find_dotenv
import json

load_dotenv(find_dotenv())


def query_sfWithin(loci_thing, sparql_endpoint, auth=None):
    '''
        auth = expects a dict with 'user' and 'password' as keys with values,
              e.g. { 'user': 'username', 'password': 'passwordhere' }
    '''
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX dct: <http://purl.org/dc/terms/>
        select ?st ?link ?par
        where {{
            ?st dct:isPartOf ?lk ;
                rdf:subject {loci_subject} ;
                rdf:predicate geo:sfWithin ;
                rdf:object ?par .
        }}
    '''.format(loci_subject=loci_thing)
    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #print(json.dumps(results, indent=4, sort_keys=True))

    matching_list = []
    for r in results["results"]["bindings"]:
        if 'par' in r:
            matching_list.append(r['par']['value'])

    #do something    
    return matching_list


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

    matches = query_sfWithin(obj['id'], SPARQL_ENDPOINT, auth=auth)
    print(matches)
    print(obj["matches"])

    assert all([a == b for a, b in zip(matches, obj['matches'])])

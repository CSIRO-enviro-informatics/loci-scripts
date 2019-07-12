from SPARQLWrapper import SPARQLWrapper, JSON
import pytest
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def test_loci_count():
    """Test integrity of LOCI cache statement counts

    1573077 statements for mb16cc
    
    TODO: GNAF, Geofabric, rest of ASGS ...
    """
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

    sparql = SPARQLWrapper(SPARQL_ENDPOINT)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    sparql.setQuery("""
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX o: <http://www.w3.org/1999/02/22-rdf-syntax-ns#object>
        PREFIX p: <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate>
        PREFIX s: <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject>
        select  (count( ?stmt) as ?count)
        where { 
	        ?stmt dct:isPartOf <http://linked.data.gov.au/dataset/mb16cc> .
            ?stmt o: ?o .
            ?stmt p: ?p .
	        ?stmt s: ?s .
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)
    
    count_mb_stmt = results["results"]["bindings"][0]['count']['value']
    assert int(count_mb_stmt) == 1573077    

   
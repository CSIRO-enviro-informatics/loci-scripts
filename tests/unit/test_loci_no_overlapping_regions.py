from SPARQLWrapper import SPARQLWrapper, JSON
import pytest
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def test_no_overlapping_gf_contracted_catchments():
    """Test integrity of LOCI cache statement counts

    Test that there are no overlapping contracted catchments
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
        PREFIX void: <http://rdfs.org/ns/void#>
        PREFIX loci: <http://linked.data.gov.au/def/loci#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX dct: <http://purl.org/dc/terms/>
        prefix dbp: <http://dbpedia.org/property/>
        PREFIX nv: <http://qudt.org/schema/qudt#numericValue>
        PREFIX qu: <http://qudt.org/schema/qudt#unit>
        PREFIX asgs: <http://linked.data.gov.au/def/asgs#>
        PREFIX data: <http://linked.data.gov.au/def/datatype/> 
        PREFIX geox: <http://linked.data.gov.au/def/geox#>
        PREFIX g: <http://linked.data.gov.au/dataset/gnaf/address/>
        SELECT (count(?s) as ?count)
        WHERE {
            ?s dct:isPartOf <http://linked.data.gov.au/dataset/mb16cc> ;
            rdf:subject ?cc1 ;
            rdf:predicate geo:sfContains ;
            rdf:object ?cc2 .
            ?cc1 a <http://linked.data.gov.au/def/geofabric#ContractedCatchment> .
            ?cc2 a <http://linked.data.gov.au/def/geofabric#ContractedCatchment>
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)
    
    count_stmt = results["results"]["bindings"][0]['count']['value']
    assert int(count_stmt) == 0

def test_no_overlapping_asgs16_mb():
    """Test integrity of LOCI cache statement counts

    Test that there are no overlapping contracted catchments
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
        PREFIX void: <http://rdfs.org/ns/void#>
        PREFIX loci: <http://linked.data.gov.au/def/loci#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX dct: <http://purl.org/dc/terms/>
        prefix dbp: <http://dbpedia.org/property/>
        PREFIX nv: <http://qudt.org/schema/qudt#numericValue>
        PREFIX qu: <http://qudt.org/schema/qudt#unit>
        PREFIX asgs: <http://linked.data.gov.au/def/asgs#>
        PREFIX data: <http://linked.data.gov.au/def/datatype/> 
        PREFIX geox: <http://linked.data.gov.au/def/geox#>
        PREFIX g: <http://linked.data.gov.au/dataset/gnaf/address/>
        SELECT (count(?s) as ?count)
        WHERE {
            ?s dct:isPartOf <http://linked.data.gov.au/dataset/mb16cc> ;
            rdf:subject ?mb1 ;
            rdf:predicate geo:sfContains ;
            rdf:object ?mb2 .
            ?mb1 a asgs:MeshBlock .
            ?mb2 a asgs:MeshBlock
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)
    
    count_stmt = results["results"]["bindings"][0]['count']['value']
    assert int(count_stmt) == 0

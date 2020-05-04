import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from pyloci.sparql import util

def test_loci_linkset_source_target_diff():
    """Test integrity of LOCI Linkset source/targets in cache
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
        PREFIX loci: <http://linked.data.gov.au/def/loci#>
        PREFIX void: <http://rdfs.org/ns/void#>
        SELECT *
        WHERE {
            ?linkset a loci:Linkset .
            ?linkset void:subjectsTarget ?subjectsTarget .
            ?linkset void:objectsTarget ?objectsTarget .
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    validFlag = True
    invalidLinksets = []
    for res in results["results"]["bindings"]:
        # if subjectsTarget == objectsTarget, then linkset is invalid
        if res['subjectsTarget']['value'] == res['objectsTarget']['value']:
            validFlag = False
            invalidLinksets.append(res['linkset']['value'])
            print("Invalid linkset subjectTarget/objectTarget: {} / {} / {}".format(res['linkset']['value'], res['subjectsTarget']['value'],  res['objectsTarget']['value']))
    assert validFlag ==  True
from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from . import util

GRAPHDB_USER = os.getenv("GRAPHDB_USER")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")

# uncomment the following GRAPHDB_SPARQL and auth variables for test repo
#GRAPHDB_SPARQL = GRAPHDB_SPARQL_TEST
auth = None
# set auth only if .env has credentials
if(GRAPHDB_USER != None and GRAPHDB_PASSWORD != None):
    auth = { 
        "user" : GRAPHDB_USER,
        "password" : GRAPHDB_PASSWORD   
    }

labels = util.query_labels_from_locations(SPARQL_ENDPOINT, auth=auth)


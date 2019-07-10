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

loci_types = [
    "<http://linked.data.gov.au/def/geofabric#ContractedCatchment>",
    "geo:Feature",
    "hyf:HY_Catchment",
    "hyf:HY_HydroFeature",
    "<http://linked.data.gov.au/def/geofabric#RiverRegion>",
    "loci:Linkset",
    "<http://linked.data.gov.au/def/asgs#MeshBlock>",
    "geo:Geometry",
    "<http://linked.data.gov.au/def/asgs#DestinationZone>",
    "<http://linked.data.gov.au/def/asgs#NaturalResourceManagementRegion>",
    "<http://linked.data.gov.au/def/asgs#StateSuburb>",
    "<http://linked.data.gov.au/def/asgs#StateOrTerritory>",
    "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1>",
    "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel2>",
    "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel3>",
    "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel4>",
    "<http://linked.data.gov.au/def/asgs#GreaterCapitalCityStatisticalArea>"
]

#query()
#print(auth)
count_types = []
for curr in loci_types:
    count = util.query_type(curr, SPARQL_ENDPOINT, auth=auth)
    count_types.append((curr, count))

print(json.dumps(count_types, indent=4, sort_keys=True))

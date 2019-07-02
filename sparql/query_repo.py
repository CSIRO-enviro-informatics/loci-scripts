from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def query(sparql_endpoint):
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT *
        WHERE { 
            ?x ?y ?z
        }
        LIMIT 10
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    print(results)
    
def query_type(loci_type, sparql_endpoint, auth=None):
    '''
        auth = expects a dict with 'user' and 'password' as keys with values,
              e.g. { 'user': 'username', 'password': 'passwordhere' }
    '''
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX loci: <http://linked.data.gov.au/def/loci#>
        PREFIX hyf: <https://www.opengis.net/def/appschema/hy_features/hyf/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        select (count(distinct ?x) as ?count)
        where {{
            ?x a {definedtype}
        }}
    '''.format(definedtype=loci_type)
    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    count  = results["results"]["bindings"][0]['count']['value']
    print(loci_type + ", " + count)
    return count
    


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
print(auth)
count_types = []
for curr in loci_types:
    count = query_type(curr, SPARQL_ENDPOINT, auth=auth)
    count_types.append((curr, count))

print(json.dumps(count_types, indent=4, sort_keys=True))

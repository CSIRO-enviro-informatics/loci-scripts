import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def query_geofabric_cc_to_asgs2016_mb(gf_cc, asgs2016_mb, sparql_endpoint, auth=None):
    '''
        auth = expects a dict with 'user' and 'password' as keys with values,
              e.g. { 'user': 'username', 'password': 'passwordhere' }
    '''
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        PREFIX void: <http://rdfs.org/ns/void#>
        PREFIX loci: <http://linked.data.gov.au/def/loci#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX dct: <http://purl.org/dc/terms/>
        prefix dbp: <http://dbpedia.org/property/>
        PREFIX nv: <http://qudt.org/schema/qudt#numericValue>
        PREFIX qu: <http://qudt.org/schema/qudt#unit>
        SELECT distinct *
        WHERE {{
            ?s dct:isPartOf <http://linked.data.gov.au/dataset/mb16cc> ;
            rdf:subject {asgs2016_mb} ;
            rdf:predicate <http://www.opengis.net/ont/geosparql#sfWithin> ;
            rdf:object {gf_cc} .
            OPTIONAL {
                {asgs2016_mb} dbp:area [ nv: ?subArea ;
                qu: ?subUnit ] .
            }
            OPTIONAL {
                {gf_cc} dbp:area [ nv: ?objArea ;
                qu: ?objUnit ] .    
            }
        }}
    '''.format(asgs2016_mb=asgs2016_mb, gf_cc=gf_cc)
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

#@pytest.mark.parametrize("obj", testdata)
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

    matches = query_geofabric_cc_to_asgs2016_mb(obj['id'], SPARQL_ENDPOINT, auth=auth)
    print(matches)
    print(obj["matches"])

    assert all([a == b for a, b in zip(matches, obj['matches'])])

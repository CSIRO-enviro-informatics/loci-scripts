import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

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
    #print(loci_type + ", " + count)
    return count

testdata = [
    [
        "<http://linked.data.gov.au/def/geofabric#ContractedCatchment>",
        "30461"
    ],
    [
        "geo:Feature",
        "570372"
    ],
    [
        "<http://linked.data.gov.au/def/geofabric#RiverRegion>",
        "231"
    ],
    [
        "loci:Linkset",
        "4"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#MeshBlock>",
        "358007"
    ],
    [
        "geo:Geometry",
        "418217"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#DestinationZone>",
        "358007"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#NaturalResourceManagementRegion>",
        "358007"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StateSuburb>",
        "358007"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StateOrTerritory>",
        "8"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1>",
        "57489"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel2>",
        "2292"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel3>",
        "340"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel4>",
        "89"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#GreaterCapitalCityStatisticalArea>",
        "89"
    ]
]

@pytest.mark.parametrize("loci_type,count", testdata)
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

    currcount = query_type(loci_type, SPARQL_ENDPOINT, auth=auth)
    assert count == currcount
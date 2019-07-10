import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from pyloci.sparql import util


testdata = [
    [
        "<http://linked.data.gov.au/def/geofabric#ContractedCatchment>",
        "30461"
    ],
    [
        "geo:Feature",
        "17155045"
    ],
    [
        "hyf:HY_Catchment",
        "30692"
    ],
    [
        "hyf:HY_HydroFeature",
        "30692"
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
        "358009"
    ],
    [
        "geo:Geometry",
        "418220"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#DestinationZone>",
        "358009"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#NaturalResourceManagementRegion>",
        "358009"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StateSuburb>",
        "358009"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StateOrTerritory>",
        "9"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1>",
        "57490"
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

    currcount = util.count_type(loci_type, SPARQL_ENDPOINT, auth=auth)
    assert count == currcount
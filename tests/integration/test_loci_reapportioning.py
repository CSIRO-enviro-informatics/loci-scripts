import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from pyloci.sparql import util


def get_verification_data():
    data = {}
    with open('./loci-testdata/loci_type_count.json') as json_file:  
        data = json.load(json_file)        
    return data


testdata = [
    [ '<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12202179>' , '<http://linked.data.gov.au/dataset/asgs2016/meshblock/30563893800>', '725451412.929990' ]
]

@pytest.mark.parametrize("gfcc,mb,areaM2", testdata)
def test_loci_intersect_area(gfcc, mb, areaM2):
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

    res_list = util.query_intersecting_region_mb16cc(gfcc, mb, SPARQL_ENDPOINT, auth=auth)

    assert len(res_list) == 1 and 'intersectingArea' in res_list[0] and res_list[0]['intersectingArea'] == areaM2


testdata2 = [
    ['test-case-A-VIC', '<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12101547>', 8, {} ]
]

@pytest.mark.parametrize("testcase,gfcc,matchcount,matchingdata", testdata2)
def test_loci_list_of_contains_matches_for_cc(testcase,gfcc,matchcount,matchingdata):
    '''Test that the list of contains for the cc matches
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

    res_list = util.query_mb16cc_cc_to_mb("<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12101547>")

    assert len(res_list) == matchcount

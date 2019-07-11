import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from pyloci.sparql import util


testdata = [
    [ '<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12202179>' , '<http://linked.data.gov.au/dataset/asgs2016/meshblock/30563893800>', '725451412.929990' ]
]

@pytest.mark.parametrize("gfcc,mb,areaM2", testdata)
def test_loci_spot_test_intersect_area(gfcc, mb, areaM2):
    '''Test loci intersection value integrity between single gfcc and mb input
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


def get_verification_contains_data():
    data = {}
    with open('./loci-testdata/test_case_contains_result.json') as json_file:  
        data = json.load(json_file)        
    return data


#testdata2 = [
#    ['test-case-A-VIC', '<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12101547>', 8, {} ]
#]

@pytest.mark.parametrize("testcase,region,matchingdata", get_verification_contains_data())
def test_loci_list_of_contains_matches_for_cc(testcase,region,matchingdata):
    '''Test that the list of contains for the region matches
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

    #res_list = util.query_sfWithin_mb_or_cc_with_graph("<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12101547>", SPARQL_ENDPOINT, auth=auth)
    regionUri = "<" + region + ">"
    res_list = util.query_mb16cc_relation(regionUri, SPARQL_ENDPOINT, relationship="geo:sfContains", auth=auth)

    assert len(res_list) == len(matchingdata)

import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import csv
import json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from pyloci.sparql import util

def get_csvdata(fname, delim='\t'):
    with open(fname, 'r', newline='') as csv_file:
        return list(csv.DictReader(csv_file, delimiter=delim))

def id_list(data):
    return [i['testcase'] for i in data]

def input_list(data):
    return [i['input'] for i in data]

def expected(data):
    return [i['input'] for i in data]


inputdata = get_csvdata('./loci-testdata/test-case-d/input/loci-test-case-D-crossdataset.csv', delim="\t")


def run_query(uri, loci_type):
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
    #print(SPARQL_ENDPOINT)
    matches = util.query_list_objects_sfContains_matching_loci_thing(uri, loci_type, SPARQL_ENDPOINT, auth=auth)
    return matches

@pytest.mark.parametrize('testinput', inputdata, ids=id_list(inputdata))
def test_loci_topology(testinput):
    '''Test 
    '''
    print(testinput)
    #query cache back on the input data
    #print(testinput)
    #with open('./loci-testdata/test-case-d/Test-' + testinput['testcase'] + '.json') as json_file:

    inputObj = testinput['input']
    #print(inputObj)
    t = "<" + testinput['target_region_type'] + ">"

    featureTypeShortName = inputObj[0]

    #print(p)
    #print(t)
    print(inputObj)
    if t != None and inputObj != None:
        test_instance_uri = "<"  + inputObj + ">"
    
        
        with open('./loci-testdata/test-case-d/Test-' + testinput['testcase'] + '.json') as json_file:
            expecteddata = json.load(json_file)
            print(test_instance_uri)
            #print(expecteddata)
        
            #run sparql query to get the sfContains of the test_instance_uri obj
            matches = run_query(test_instance_uri, t)
            #print(matches)
            assert match_expected_data_with_matches(testinput['testcase'], expecteddata['contains'], matches, t)
    else:
        assert False


def match_expected_data_with_matches(testcase_id, expected_list, matches_sparql_list, featureTypeShortName):
    # things in matches not in expected
    diff = sorted(list(set(matches_sparql_list) - set(expected_list)))
    # things in expected not in matches
    diff2 = sorted(list(set(expected_list) - set(matches_sparql_list)))
    #print(diff)
    #print(len(diff))
    if(len(diff2) == 0):
        return True
    return False


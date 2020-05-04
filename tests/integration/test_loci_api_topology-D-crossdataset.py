import pytest
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import csv
import json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from pyloci.api import util

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

api_util = util.Util()
LOCI_INTEGRATION_API = os.getenv("LOCI_INTEGRATION_API")

def run_query(uri, loci_type):
    res  = api_util.query_api_location_overlaps(uri, loci_type, LOCI_INTEGRATION_API, crosswalk=True)
    return res


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
    t =  testinput['target_region_type'] 

    featureTypeShortName = inputObj[0]

    #print(p)
    #print(t)
    print(inputObj)
    if t != None and inputObj != None:
        test_instance_uri = inputObj 
    
        
        with open('./loci-testdata/test-case-d/Test-' + testinput['testcase'] + '.json') as json_file:
            expecteddata = json.load(json_file)
            print(test_instance_uri)
            #print(expecteddata)
        
            #run sparql query to get the sfContains of the test_instance_uri obj
            matches = run_query(test_instance_uri, t)
            #turn list of dict to plain list
            #print(matches)
            if "message" in matches:
                assert matches['code'] != 500

            list_of_matching_uris = list(map(lambda x : x['uri'], matches['overlaps']))
            #print(list_of_matching_uris)
            #print(matches)
            assert match_expected_data_with_matches(testinput['testcase'], expecteddata['contains'], list_of_matching_uris, t)
    else:
        assert False

def check_expected_data_in_matches(testcase_id, expected_list, matches_list, featureTypeShortName):
    # things in matches not in expected
    #print(expected_with_angle_brackets_list)
    diff = sorted(list(set(matches_list) - set(expected_list)))
    # things in expected not in matches
    diff2 = sorted(list(set(expected_list) - set(matches_list)))
    print(len(expected_list))
    print(len(matches_list))
    print(len(diff2))
    if(len(diff2) < len(matches_list)):
        return True
    return False

def match_expected_data_with_matches(testcase_id, expected_list, matches_list, featureTypeShortName):
    # things in matches not in expected
    #print(expected_with_angle_brackets_list)
    diff = sorted(list(set(matches_list) - set(expected_list)))
    # things in expected not in matches
    diff2 = sorted(list(set(expected_list) - set(matches_list)))
    print(diff2)
    print(len(diff2))
    if(len(diff2) == 0):
        return True
    return False


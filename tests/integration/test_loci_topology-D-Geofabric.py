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


inputdata = get_csvdata('./loci-testdata/test-case-d/input/loci-test-case-D-GF-all.csv', delim="\t")

uriPrefixes = {
    "gf-2.1" : {
        "cc": "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/",
        "rr": "http://linked.data.gov.au/dataset/geofabric/riverregion/",
        "dd": "http://linked.data.gov.au/dataset/geofabric/drainagedivision/",
    },
}

typeIdx = {
    "mb": "<http://linked.data.gov.au/def/asgs#MeshBlock>",
    "sa1": "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1>",
    "sa2": "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel2>",
    "sa3": "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel3>",
    "sa4": "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel4>",
    "ste": "<http://linked.data.gov.au/def/asgs#StateOrTerritory>",
    "cc": "<http://linked.data.gov.au/def/geofabric#ContractedCatchment>",
    "rr": "<http://linked.data.gov.au/def/geofabric#RiverRegion>",
    "dd": "<http://linked.data.gov.au/def/geofabric#DrainageDivision>",
}

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
    #print(testinput['input'])
    inputObj = json.loads(testinput['input'])
    #print(inputObj)
    target_region_type = testinput['target_region_type']

    p = uriPrefixes['gf-2.1'][inputObj[0]] if inputObj[0] in uriPrefixes['gf-2.1'] else None
    t = typeIdx[target_region_type] if target_region_type in typeIdx else None
    #print(p)
    #print(t)
    #print(len(inputObj))
    if p != None and t != None and len(inputObj) >= 2:
        test_instance_uri = "<" + p + inputObj[1] + ">"
    
        expecteddata = get_csvdata('./loci-testdata/test-case-d/Test-' + testinput['testcase'] + '.csv', delim=",")
        #print(expecteddata)
    
        #run sparql query to get the sfContains of the test_instance_uri obj
        matches = run_query(test_instance_uri, t)
        #print(matches)

        if len(matches) != len(expecteddata):
            missing_features = len(expecteddata)- len(matches) 
            print("Does not match! Missing num features = " + str(missing_features)) 
            eval_diff_and_save_to_file(testinput['testcase'], expecteddata, matches)


        #run matches against expecteddata
        assert len(matches) == len(expecteddata)


    #read expected data from file based on id
    assert True


def eval_diff_and_save_to_file(testcase_id, expected_csv_list, matches_sparql_list):
    #get list of hydroids from expected_csv_list
    expected_hydroid_list = []
    matches_hydroid_list = []
    for item in expected_csv_list:
        expected_hydroid_list.append(item["HydroID"])

    for item in matches_sparql_list:
        m_hydroid = item.rsplit('/', 1)[-1]
        matches_hydroid_list.append(m_hydroid)

    # things in matches not in expected
    diff = sorted(list(set(matches_hydroid_list) - set(expected_hydroid_list)))
    # things in expected not in matches
    diff2 = sorted(list(set(expected_hydroid_list) - set(matches_hydroid_list)))

    fname = './loci-testdata/test-case-d/Testoutput-' + testcase_id + '.csv'
    print("Output to file: " + fname)
    with open(fname, 'w', newline='') as csvfile:
        fieldnames = ['hydroid', 'source']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for x in diff:
            writer.writerow({'hydroid': x, 'source': 'matches_in_cache_not_in_testdata'})
        for y in diff2:
            writer.writerow({'hydroid': y, 'source': 'expected_hydroid_in_testdata_but_is_missing_in_cache'})

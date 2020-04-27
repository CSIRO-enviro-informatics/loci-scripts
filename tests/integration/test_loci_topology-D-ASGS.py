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


inputdata = get_csvdata('./loci-testdata/test-case-d/input/loci-test-case-D-ASGS-all.csv', delim="\t")

uriPrefixes = {
    "asgs2016" : {
        "mb": "http://linked.data.gov.au/dataset/asgs2016/meshblock/",
        "sa1": "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel1/",
        "sa2": "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel2/",
        "sa3": "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel3/",
        "sa4": "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel4/",
        "ste": "http://linked.data.gov.au/dataset/asgs2016/stateorterritory/",
    },
}

typeIdx = {
    "mb": "<http://linked.data.gov.au/def/asgs#MeshBlock>",
    "sa1": "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1>",
    "sa2": "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel2>",
    "sa3": "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel3>",
    "sa4": "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel4>",
    "ste": "<http://linked.data.gov.au/def/asgs#StateOrTerritory>",
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

    p = uriPrefixes['asgs2016'][inputObj[0]] if inputObj[0] in uriPrefixes['asgs2016'] else None
    t = typeIdx[target_region_type] if target_region_type in typeIdx else None
    #print(p)
    #print(t)
    #print(len(inputObj))
    if p != None and t != None and len(inputObj) >= 2:
        test_instance_uri = "<" + p + inputObj[1] + ">"
    
        expecteddata = get_csvdata('./loci-testdata/test-case-d/Test-' + testinput['testcase'] + '.csv', delim=",")
        print(test_instance_uri)
        print(expecteddata)
    
        #run sparql query to get the sfContains of the test_instance_uri obj
        matches = run_query(test_instance_uri, t)
        #print(matches)

        #run matches against expecteddata
        assert len(matches) == len(expecteddata)


    #read expected data from file based on id
    assert True


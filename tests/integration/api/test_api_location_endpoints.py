import pytest
import requests
import os
import csv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

LOCI_INTEGRATION_API = os.getenv("LOCI_INTEGRATION_API")

ADDRESS_TYPE = "http://linked.data.gov.au/def/gnaf#Address"
MB_TYPE = "http://linked.data.gov.au/def/asgs#MeshBlock"
CC_TYPE = "http://linked.data.gov.au/def/geofabric#ContractedCatchment"
LGA_TYPE = "http://linked.data.gov.au/def/asgs#LocalGovernmentArea"
SA1_TYPE = "http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1"


PREFIXES = {
    "sa1" : "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel1/",
    "sa2" : "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel2/",
    "sa3" : "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel3/",
    "sa4" : "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel4/",
    "lga" : "http://linked.data.gov.au/dataset/asgs2016/localgovernmentarea/"
}

TEST_DATA = [
    {
        "fromFeature" : PREFIXES['sa1'] + "20604112205",
        "toFeatureType" : "http://linked.data.gov.au/def/asgs#MeshBlock",
        "contains" : ['http://linked.data.gov.au/dataset/asgs2016/meshblock/20664550000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20401330000']
    },
    {
        "fromFeature" : PREFIXES['sa1'] + "20604112224",
        "toFeatureType" : "http://linked.data.gov.au/def/asgs#MeshBlock",
        "contains" : [
            'http://linked.data.gov.au/dataset/asgs2016/meshblock/20664390000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20664410000', 
            'http://linked.data.gov.au/dataset/asgs2016/meshblock/20664440000', 
             'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393202000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393201000', 
            'http://linked.data.gov.au/dataset/asgs2016/meshblock/20664400000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20664420000'
        ]
    },
    {
        "fromFeature" : PREFIXES['sa1'] + "20604112230",
        "toFeatureType" : "http://linked.data.gov.au/def/asgs#MeshBlock",
        "contains" : [
            'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393160000', 
            'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393750000', 
            'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393540000', 
            'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393670000', 
            'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393830000'
            ]
    },
    {
        "fromFeature" : PREFIXES['sa1'] + "20604112231",
        "toFeatureType" : "http://linked.data.gov.au/def/asgs#MeshBlock",
        "contains" : ['http://linked.data.gov.au/dataset/asgs2016/meshblock/20394570000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393972000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393931000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393971000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20394010000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20394580000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20394000000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393932000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393680000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20664430000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393990000']
    },
    {
        "fromFeature" : PREFIXES['sa1'] + "20604112232",
        "toFeatureType" : "http://linked.data.gov.au/def/asgs#MeshBlock",
        "contains" : ['http://linked.data.gov.au/dataset/asgs2016/meshblock/20394030000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393690000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20393100000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20394060000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20394020000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20394040000', 'http://linked.data.gov.au/dataset/asgs2016/meshblock/20394050000']
    }
]


TEST_LIST_LGA_TO_SA1 = [ "11800" , "24970", "29399", "31000" ]

def query_api_location(fromFeature, toFeatureType, api_endpoint, api_modifier='overlaps', crosswalk='false'):
    '''
    '''
    
    payload = {
        "uri": fromFeature,
        "areas" : "true",
        "proportion" : "true", 
        "contains" : "false",
        "within" : "false",
        "output_type" : toFeatureType,
        "crosswalk" : crosswalk,
        "count" : 1000,
        "offset" : 0
    }


    print(payload)

    url = api_endpoint + "/location/" + api_modifier
    r = requests.get(url, params=payload)
    j = r.json()
    return j


def get_csvdata(fname, delim='\t'):
    with open(fname, 'r', newline='') as csv_file:
        return list(csv.DictReader(csv_file, delimiter=delim))

def id_list(data):
    return [i['testcase'] for i in data]

def input_list(data):
    return [i['input'] for i in data]

def expected(data):
    return [i['input'] for i in data]


inputdata = get_csvdata('./loci-testdata/excelerator/population-sa1-test.csv', delim=",")

def loci_relations(obj):
    return {}

@pytest.mark.parametrize("item", TEST_DATA)
def test_api_location_contains_sa1_mb(item):
    api_endpoint = LOCI_INTEGRATION_API
    #data = query_api_location(item['fromFeature'], item['toFeatureType'], api_endpoint, api_modifier='overlaps', crosswalk='false')
    #print(data)
    print(item['fromFeature'])
    data = query_api_location(item['fromFeature'], item['toFeatureType'], api_endpoint, api_modifier='contains', crosswalk='false')
    assert (sorted(item['contains']) == sorted(data['locations']))

@pytest.mark.parametrize("lga_id", TEST_LIST_LGA_TO_SA1)
def test_api_location_contains_sa1_mb_same_base_walk(lga_id):
    api_endpoint = LOCI_INTEGRATION_API

    #data = query_api_location(item['fromFeature'], item['toFeatureType'], api_endpoint, api_modifier='overlaps', crosswalk='false')
    #print(data)

    fromFeature = PREFIXES['lga'] + lga_id
    toFeatureType = SA1_TYPE

    expecteddata = get_csvdata('./loci-testdata/test-case-intra-dataset-overlaps/asgs16_lga_to_sa1-' + lga_id + '.csv', delim=",")
    print("Expected data length: {}".format(len(expecteddata)))
    data = query_api_location(fromFeature, toFeatureType, api_endpoint, api_modifier='overlaps', crosswalk='true')
    
    print(data)

    assert len(data) > 0

    assert len(data['overlaps']) == len(expecteddata)

    #list_contains = []

    #assert (sorted(item['contains']) == sorted(data['locations']))

def main():
    api_endpoint = LOCI_INTEGRATION_API
    for item in TEST_DATA:
        #data = query_api_location(item['fromFeature'], item['toFeatureType'], api_endpoint, api_modifier='overlaps', crosswalk='false')
        #print(data)
        print(item['fromFeature'])
        data = query_api_location(item['fromFeature'], item['toFeatureType'], api_endpoint, api_modifier='contains', crosswalk='false')
        print(data)

if __name__ == "__main__":
    # execute only if run as a script
    main()

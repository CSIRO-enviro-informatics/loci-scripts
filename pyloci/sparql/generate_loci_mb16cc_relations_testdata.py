from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
import csv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from pyloci.sparql import util


def parse_input_file(csvfile):   
    test_list = []
    with open(csvfile, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                #print(f'Column names are {", ".join(row)}')
                line_count += 1
            
            #print(f'{row["testcase"]} {row["uri"]}')
            test_list.append((row["testcase"], row["uri"].strip()))
            line_count += 1
        #print(f'Processed {line_count} lines.')
    return test_list

GRAPHDB_USER = os.getenv("GRAPHDB_USER")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")

# uncomment the following GRAPHDB_SPARQL and auth variables for test repo
#GRAPHDB_SPARQL = GRAPHDB_SPARQL_TEST
auth = None
# set auth only if .env has credentials
if(GRAPHDB_USER != None and GRAPHDB_PASSWORD != None):
    auth = { 
        "user" : GRAPHDB_USER,
        "password" : GRAPHDB_PASSWORD   
    }

#loci_cc_list = [
#    "<http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12105140>"
#]
test_case_file = "./loci-testdata/test_case_uris.csv"
#outfile = "./loci-testdata/test_case_withins.csv"
loci_cc_list = parse_input_file(test_case_file)
#print(loci_cc_list)

#query()
#print(auth)
matches = []
test_case_withins_list = {}

for (testcase,uristr) in loci_cc_list:
    uri = "<" + uristr + ">"
    #print(testcase)
    #print(uristr)
    #withins_list = util.query_sfWithin(uri, SPARQL_ENDPOINT, auth=auth)
    withins_list = util.query_sfWithin_mb_or_cc_with_graph(uri, SPARQL_ENDPOINT, auth=auth)
    if testcase in test_case_withins_list:
        test_case_withins_list[testcase][uristr] = withins_list
    else:
        test_case_withins_list[testcase] = {}
        test_case_withins_list[testcase][uristr] = withins_list

    #for fromURI,matching_withins in withins_list:
    #    print(fromURI + "," + matching_withins)
    #print(json.dumps(withins_list, indent=4, sort_keys=True))

    
print(json.dumps(test_case_withins_list, indent=4, sort_keys=False))

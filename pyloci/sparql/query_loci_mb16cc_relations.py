from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
import csv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def query_sfWithin(locationUri, sparql_endpoint, auth=None):
    '''
        auth = expects a dict with 'user' and 'password' as keys with values,
              e.g. { 'user': 'username', 'password': 'passwordhere' }
    '''
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    cc = '?cc'
    mb = '?mb'
    if 'asgs2016/meshblock' in locationUri:
        mb = locationUri
        filterStmt = 'FILTER (?mb = ' + mb + ')'
    elif 'geofabric/contractedcatchment' in locationUri:
        cc = locationUri
        filterStmt = 'FILTER (?cc = ' + cc + ')'

    query = '''
        PREFIX void: <http://rdfs.org/ns/void#>
        PREFIX loci: <http://linked.data.gov.au/def/loci#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX dct: <http://purl.org/dc/terms/>
        prefix dbp: <http://dbpedia.org/property/>
        PREFIX nv: <http://qudt.org/schema/qudt#numericValue>
        PREFIX qu: <http://qudt.org/schema/qudt#unit>
        PREFIX asgs: <http://linked.data.gov.au/def/asgs#>
        PREFIX data: <http://linked.data.gov.au/def/datatype/> 
        PREFIX geox: <http://linked.data.gov.au/def/geox#>
        PREFIX g: <http://linked.data.gov.au/dataset/gnaf/address/>
        SELECT DISTINCT ?mb ?cc ?pred ?mbArea ?ccArea ?mbAreaGraph ?ccAreaGraph
        WHERE {{
            ?s dct:isPartOf <http://linked.data.gov.au/dataset/mb16cc> ;
            rdf:subject ?mb ;
            rdf:predicate ?pred ;
            rdf:object ?cc .
            ?mb a asgs:MeshBlock .
            ?cc a <http://linked.data.gov.au/def/geofabric#ContractedCatchment>
            GRAPH ?mbAreaGraph {{
                OPTIONAL {{
                    ?mb geox:hasAreaM2 [ data:value ?mbArea ] .
                }}
            }}
            GRAPH ?ccAreaGraph {{
                OPTIONAL {{
                    ?cc geox:hasAreaM2 [ 
                        data:value ?ccArea ;
                    ] .                
                }}
            }}
            {filterStmt}
        }}
    '''.format(filterStmt=filterStmt)
    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #print(json.dumps(results, indent=4, sort_keys=True))

    withins_list = []
    for res in results['results']['bindings']:
        #print(json.dumps(res, indent=4, sort_keys=True))
        #print(res['mb']['value'] + "," + res['cc']['value'])
        #encode <from URI, URI matching withins for from URI>
        withins_list.append( {
                    'mb': res['mb']['value'], 
                    'pred' : res['pred']['value'], 
                    'cc': res['cc']['value'], 
                    'mbArea': res['mbArea']['value'], 
                    'ccArea' : res['ccArea']['value'],
                    'mbAreaGraph': res['mbAreaGraph']['value'], 
                    'ccAreaGraph' : res['ccAreaGraph']['value']
                }
            )

    #do something    
    return withins_list

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
    withins_list = query_sfWithin(uri, SPARQL_ENDPOINT, auth=auth)
    if testcase in test_case_withins_list:
        test_case_withins_list[testcase][uristr] = withins_list
    else:
        test_case_withins_list[testcase] = {}
        test_case_withins_list[testcase][uristr] = withins_list

    #for fromURI,matching_withins in withins_list:
    #    print(fromURI + "," + matching_withins)
    #print(json.dumps(withins_list, indent=4, sort_keys=True))

    
print(json.dumps(test_case_withins_list, indent=4, sort_keys=False))

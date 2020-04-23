import pytest
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from pyloci.sparql import util

LOCI_INTEGRATION_API = os.getenv("LOCI_INTEGRATION_API")

ADDRESS_TYPE = "http://linked.data.gov.au/def/gnaf#Address"
MB_TYPE = "http://linked.data.gov.au/def/asgs#MeshBlock"
CC_TYPE = "http://linked.data.gov.au/def/geofabric#ContractedCatchment"

PREFIXES = {
    "sa1" : "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel1/",
    "sa2" : "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel2/",
    "sa3" : "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel3/",
    "sa4" : "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel4/",
    "mb" : "http://linked.data.gov.au/dataset/asgs2016/meshblock/"
}


def query_type(featureType, limit, offset):
    '''
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

    return util.list_type_instances(featureType, SPARQL_ENDPOINT, limit=limit, offset=offset, auth=auth)
    
def query_type_by_instance_prefix(featureType, loci_instance_prefix, limit, offset):
    '''
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

    return util.list_type_instances_by_uristring(featureType, loci_instance_prefix, SPARQL_ENDPOINT, limit=limit, offset=offset, auth=auth)
    



def main():
    max_page_size = 100000
    #max_total_res = 50
    total_res_count = 0    

    #while total_res_count <= max_total_res:
    while True:
        #reslist = query_type_by_instance_prefix(MB_TYPE, PREFIXES['mb'], limit=max_page_size, offset=total_res_count)        
        reslist = query_type(MB_TYPE, limit=max_page_size, offset=total_res_count)        
        if(len(reslist) <= 0):
            break
        for uri in reslist:
            print(uri)
        total_res_count = len(reslist) + total_res_count
        


    

if __name__ == "__main__":
    # execute only if run as a script
    main()

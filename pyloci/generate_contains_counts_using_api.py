from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

LOCI_INTEGRATION_API = os.getenv("LOCI_INTEGRATION_API")


GRAPHDB_USER = os.getenv("GRAPHDB_USER")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")


from pyloci.api.util import Util as API_Util
from pyloci.sparql import util as sparql_util


auth = None
api_util = API_Util()
    
#Query for a list of all source feature type
def query_list_of_source_feature_type(source_feature_type_shortlabel, max=100000):
    source_feature_type = api_util.get_datatype_uri_via_shortlabel(source_feature_type_shortlabel)
    #print(source_feature_type)
    res = sparql_util.list_type_instances(source_feature_type, SPARQL_ENDPOINT, limit=max)
    return res

def query_target_features(source_feature_uri, target_feature_type_shortlabel, target_dataset_uri):
    '''
    Returns a list of target feature types for source feature uri
    '''
    #url = api_endpoint + "/location/" + api_modifier
    fromFeature = source_feature_uri    
    list_locations = api_util.query_api_location_contains(fromFeature, LOCI_INTEGRATION_API)    
    #print(list_locations)
    list_targets = []
    if 'locations' in list_locations:
        #filter list of mb by prefix of instances
        for uri in list_locations['locations']:
            datatype_instance_prefix = api_util.get_namespace_prefix_for_datatype_via_shortlabel(target_feature_type_shortlabel, target_dataset_uri)
            #print(uri)

            if str(uri).startswith(datatype_instance_prefix):
                list_targets.append(uri)

        return list_targets
    return None


def main(source_feature_type_shortlabel, target_feature_type_shortlabel, source_dataset=None, target_dataset_uri=None, num_source_features=1000000):
    source_list = query_list_of_source_feature_type(source_feature_type_shortlabel, max=num_source_features)
    target_dict = {}


    for s in source_list:
        #store counts for now    
        target_list = query_target_features(s, target_feature_type_shortlabel, target_dataset_uri)
        target_count = len(target_list)
        target_dict[s] = target_count
        
    print(json.dumps(target_dict, indent=4, sort_keys=True))

import sys, argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Loc-I Contains Counts')
    parser.add_argument('source_feature_type_shortlabel', help='Shortlabel for the source featuretype like \'sa1\'.')
    parser.add_argument('target_feature_type_shortlabel', help='Shortlabel for the target featuretype like \'mb\'.')
    parser.add_argument('--source-dataset-uri', dest='source_dataset', help='Source dataset URI')
    parser.add_argument('--target-dataset-uri', dest='target_dataset',help='Target dataset URI')
    parser.add_argument('--num-source-features', dest='num_source_features',help='Max number of source features')


    args = parser.parse_args()
    source_dataset = None
    if args.source_dataset:
        source_dataset = args.source_dataset
    target_dataset = None
    if args.target_dataset:
        target_dataset = args.target_dataset
    num_source_features = 1000000
    if args.num_source_features:
        num_source_features = args.num_source_features

    main(args.source_feature_type_shortlabel, args.target_feature_type_shortlabel, source_dataset, target_dataset, num_source_features)
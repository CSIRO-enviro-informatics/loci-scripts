from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
import urllib
import time
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
    print(source_feature_type)
    res = sparql_util.list_type_instances(source_feature_type, SPARQL_ENDPOINT, limit=max)
    return res

def stringify_uri_to_filename(uri):
    return urllib.parse.quote_plus(uri.replace("/","_").replace(":", "_"))



def query_target_features(source_feature_uri, target_feature_type_shortlabel, target_dataset_uri, output_filename=None):
    '''
    Returns a list of target feature types for source feature uri
    '''
    #url = api_endpoint + "/location/" + api_modifier
    fromFeature = source_feature_uri    
    print(fromFeature)
    
    toFeatureType = api_util.get_datatype_uri_via_shortlabel(target_feature_type_shortlabel, target_dataset_uri)

    print("Querying overlaps of {} to {}...".format(fromFeature, toFeatureType))
    tic = time.perf_counter()
    list_locations = api_util.query_api_location_overlaps(fromFeature, toFeatureType, LOCI_INTEGRATION_API, crosswalk='true')
    toc = time.perf_counter()
    print(f"query_api_location_overlaps took {toc - tic:0.4f} seconds")

    
    #write this to file
    if(output_filename == None):
        filename = "overlaps_to_{}_{}.json".format(target_feature_type_shortlabel, stringify_uri_to_filename(source_feature_uri))
    else:
        filename = output_filename
    with open(filename, 'w') as outfile:
        print("Writing to: " + filename)
        json.dump(list_locations, outfile, indent=4)
        
    return 


def main(source_feature_type_shortlabel, target_feature_type_shortlabel, source_dataset=None, target_dataset_uri=None, 
            num_source_features=1000000, single_source_uri=None, output_filename=None):
    target_dict = {}

    if single_source_uri != None:
        print("Querying source {}...".format(single_source_uri))
        query_target_features(single_source_uri, target_feature_type_shortlabel, target_dataset_uri, output_filename)
        return

    source_list = query_list_of_source_feature_type(source_feature_type_shortlabel, max=num_source_features)
    num_sources = len(source_list)
    i = 0
    for s in source_list:
        i = i + 1
        #store counts for now    
        print("Querying source {} of {}...".format(i, num_sources))
        query_target_features(s, target_feature_type_shortlabel, target_dataset_uri, output_filename)
    return
        
import sys, argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Loc-I Contains Counts')
    parser.add_argument('source_feature_type_shortlabel', help='Shortlabel for the source featuretype like \'sa1\'.')
    parser.add_argument('target_feature_type_shortlabel', help='Shortlabel for the target featuretype like \'mb\'.')
    parser.add_argument('--source-dataset-uri', dest='source_dataset', help='Source dataset URI')
    parser.add_argument('--single-source-instance-uri', dest='single_source_uri', help='Run for a single source dataset instance URI')
    parser.add_argument('--target-dataset-uri', dest='target_dataset',help='Target dataset URI')
    parser.add_argument('--output', dest='output_filename',help='Target output file')
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
    single_source_uri = None
    if args.single_source_uri:
        single_source_uri = args.single_source_uri
    output_filename = None
    if args.output_filename:
        output_filename = args.output_filename

    main(args.source_feature_type_shortlabel, args.target_feature_type_shortlabel, source_dataset, target_dataset, num_source_features, single_source_uri, output_filename)
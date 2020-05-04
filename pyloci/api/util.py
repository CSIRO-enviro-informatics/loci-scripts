import requests

LOCI_DATATYPES_STATIC_JSON = "https://loci.cat/json-ld/loci-types.json"

class Util:
    DATATYPES_IDX_BY_SHORTLABEL_DEFAULT = {}
    DATATYPES_IDX_BY_SHORTLABEL = {}
    DATATYPES_IDX_BY_PREFIX = {}
    DATATYPES_IDX_BY_URI = {}
    DATATYPES_IDX_BY_DATASET = {}
    DATATYPES_BASE = []
    DATATYPES_BASE_IDX_BY_DATASET_URI = {}
    DATATYPES_BASE_IDX_BY_DATASET_PREFIX = {}
    DATATYPES = []

    def __init__(self):
        #grab the list from API                
            url = LOCI_DATATYPES_STATIC_JSON
            r = requests.get(url)
            #print(r.status_code)
            if r.status_code in [200]:
                self.DATATYPES = r.json()
                for item in self.DATATYPES:
                    # map prefix _to_ datatype
                    self.DATATYPES_IDX_BY_PREFIX[item['prefix']] = item
                    # map shortlabel _to_ datatype
                    self.DATATYPES_IDX_BY_SHORTLABEL_DEFAULT[item['shortlabel']] = item

                    if item['datasetUri'] not in self.DATATYPES_IDX_BY_DATASET:
                        self.DATATYPES_IDX_BY_DATASET[item['datasetUri']] = { item['uri'] :  item['shortlabel'] }
                    else:
                        self.DATATYPES_IDX_BY_DATASET[item['datasetUri']][item['uri']] = item['shortlabel']

                    if item['datasetUri'] not in self.DATATYPES_IDX_BY_SHORTLABEL:
                        self.DATATYPES_IDX_BY_SHORTLABEL[item['datasetUri']] = { item['shortlabel'] :  item }
                    else:
                        self.DATATYPES_IDX_BY_SHORTLABEL[item['datasetUri']][item['shortlabel']] = item
                    # map URI of datatype _to_ datatype obj
                    if item['uri'] not in self.DATATYPES_IDX_BY_URI:
                        self.DATATYPES_IDX_BY_URI[item['uri']] = { item['datasetUri'] :  item }
                    else:
                        self.DATATYPES_IDX_BY_URI[item['uri']][item['datasetUri']] = item
                #get the relevant basetype                 
                self.DATATYPES_BASE = list(filter(lambda i: ('baseType' in i and i['baseType'] == True), self.DATATYPES)) 
                for item in self.DATATYPES_BASE:
                    # map curr dataset prefix to basetype
                    self.DATATYPES_BASE_IDX_BY_DATASET_PREFIX[item['prefix']] = item
                    # map curr uri prefix to basetype
                    self.DATATYPES_BASE_IDX_BY_DATASET_URI[item['datasetUri']] = item
            else:
                print("Error in getting {}. Status code is not 200".format(url))

            
        #except Exception:
        #    print("Error in getting {}. Something went wrong".format(url))

    def get_namespace_prefix_for_datatype_via_uri(self, datatype_uri, dataset_uri=None):
        if dataset_uri != None:
            return self.DATATYPES_IDX_BY_SHORTLABEL[dataset_uri][datatype_uri]['prefix']
        return self.DATATYPES_IDX_BY_SHORTLABEL_DEFAULT[datatype_uri]['prefix']

    def get_namespace_prefix_for_datatype_via_shortlabel(self, shortlabel, dataset_uri=None):
        if dataset_uri != None:
            return self.DATATYPES_IDX_BY_SHORTLABEL[dataset_uri][shortlabel]['prefix']
        return self.DATATYPES_IDX_BY_SHORTLABEL_DEFAULT[shortlabel]['prefix']
    
    def get_datatype_uri_via_shortlabel(self, shortlabel, dataset_uri=None):
        if dataset_uri != None:
            return self.DATATYPES_IDX_BY_SHORTLABEL[dataset_uri][shortlabel]['uri']
        return self.DATATYPES_IDX_BY_SHORTLABEL_DEFAULT[shortlabel]['uri']
        
    def get_datatype_uris(self, dataset_uri=None):
        if dataset_uri != None:
            dict_datatypes = self.DATATYPES_IDX_BY_DATASET[dataset_uri]
            #return list(dict_datatypes.values())
            return self.DATATYPES_IDX_BY_DATASET[dataset_uri]
        return self.DATATYPES_IDX_BY_DATASET

    def query_api_location_overlaps(self, fromFeature, toFeatureType, api_endpoint, crosswalk='false'):
        '''
        '''    
        if(crosswalk == True):
           crosswalk = 'true'
        if(crosswalk == False):
           crosswalk = 'false'
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
        #print(payload)
        url = api_endpoint + "/location/overlaps"
        r = requests.get(url, params=payload, timeout=None)
        j = r.json()
        return j

    def query_api_location_contains(self, fromFeature, api_endpoint):
        '''
        '''    
        payload = {
            "uri": fromFeature,
            "count": 10000000
        }

        url = api_endpoint + "/location/contains"
        r = requests.get(url, params=payload, timeout=None)
        j = r.json()
        return j

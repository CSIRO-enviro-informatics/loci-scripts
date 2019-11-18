import argparse
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF
import os
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper import SPARQLWrapper2

import re


GRAPHDB_USER = os.getenv("GRAPHDB_USER")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")

testdata_uris = [
    "http://linked.data.gov.au/dataset/asgs2016/meshblock/20663970000", #mb in french island    
    "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel1/20503108801",
    "http://linked.data.gov.au/dataset/asgs2016/stateorterritory/2",
    "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel2/205031088",
    "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel3/20503",
    "http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel4/205",
    "http://linked.data.gov.au/dataset/geofabric/contractedcatchment/12101547",
    "http://linked.data.gov.au/dataset/geofabric/drainagedivision/9400210",
    "http://linked.data.gov.au/dataset/geofabric/riverregion/9400345",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/address/GAVIC411436309",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/address/GAVIC411457963",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/address/GAVIC412676812",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/address/GAVIC412676813",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/address/GAVIC412678961",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/address/GAVIC412678963",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/address/GAVIC425683387",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/addressSite/411591483",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/locality/VIC943",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/streetLocality/VIC2021622",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/addressSite/411597020",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/streetLocality/VIC2047702",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/addressSite/412831053",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/streetLocality/VIC2050994",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/addressSite/412831054",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/streetLocality/VIC2047702",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/addressSite/412831149",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/streetLocality/VIC2021808",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/addressSite/412831151",
    "http://linked.data.gov.au/dataset/gnaf-2016-05/streetLocality/VIC2047702"
]

def fetch_linked_data_ttl_from_source():
    g = Graph()
    for uri in testdata_uris:
        print("Getting URI via HTTP GET: " + uri)
        try:
            g.parse(uri)
        except Exception as e:
            print("something went wrong when fetching " + uri)
            print(str(e))
            print("trying to continue...")
    return g

def fetch_linksets_from_cache():
    #iterate over uris, find base uri and get linkset    
    g = Graph()
    for uri in testdata_uris:
        if(re.search("/address/|/contractedcatchment/|/meshblock/", uri) ):
            print("Uri matches base pattern " + uri)
            g = query_cache_for_linkset(uri, g)
            g = query_cache_for_linkset_reverse(uri, g)
    return g

def query_cache_for_linkset(current_uri, g):
    query = """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX loci: <http://linked.data.gov.au/def/loci#>
PREFIX o: <http://www.w3.org/1999/02/22-rdf-syntax-ns#object>
PREFIX p: <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate>
PREFIX s: <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject>
SELECT ?stmt ?to ?from ?pred ?linksetInstance 
WHERE {{
    ?stmt dct:isPartOf ?linksetInstance .
    ?linksetInstance a loci:Linkset .
    ?stmt o: ?to .
    ?stmt p: ?pred .
    ?stmt s: ?from  .
    ?stmt ?x ?y
    FILTER(?from = <{current_uri}>)
}}
    """.format(current_uri=current_uri)
    sparql = SPARQLWrapper2(SPARQL_ENDPOINT)
    sparql.setQuery(query)
    
    for result in sparql.query().bindings:
        stmt = result["stmt"]
        from_uri = result["from"]
        to_uri = result["to"]
        pred= result["pred"]
        linksetInstance = result["linksetInstance"]

        partOf = URIRef("http://purl.org/dc/terms/isPartOf")

        stmt_node = None
        if(stmt.type == 'uri'):
            stmt_node = URIRef(stmt.value)
        else:
            stmt_node = BNode() # a GUID is generated

        to_node = URIRef(to_uri.value)
        from_node = URIRef(from_uri.value)
        pred_node = URIRef(pred.value)
        linkset_node = URIRef(linksetInstance.value)

        g.add( (stmt_node, RDF.object, to_node) )
        g.add( (stmt_node, RDF.subject, from_node) )
        g.add( (stmt_node, RDF.predicate, pred_node) )
        g.add( (stmt_node, partOf, linkset_node) )
        g.add( (linkset_node, RDF.type, URIRef("http://linked.data.gov.au/def/loci#Linkset")) )

    return g

def query_cache_for_linkset_reverse(current_uri, g):
    query = """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX loci: <http://linked.data.gov.au/def/loci#>
PREFIX o: <http://www.w3.org/1999/02/22-rdf-syntax-ns#object>
PREFIX p: <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate>
PREFIX s: <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject>
SELECT ?stmt ?to ?from ?pred ?linksetInstance 
WHERE {{
    ?stmt dct:isPartOf ?linksetInstance .
    ?linksetInstance a loci:Linkset .
    ?stmt o: ?to .
    ?stmt p: ?pred .
    ?stmt s: ?from  .
    ?stmt ?x ?y
    FILTER(?to = <{current_uri}>)
}}
    """.format(current_uri=current_uri)
    sparql = SPARQLWrapper2(SPARQL_ENDPOINT)
    sparql.setQuery(query)
    
    for result in sparql.query().bindings:
        stmt = result["stmt"]
        from_uri = result["from"]
        to_uri = result["to"]
        pred= result["pred"]
        linksetInstance = result["linksetInstance"]

        partOf = URIRef("http://purl.org/dc/terms/isPartOf")

        stmt_node = None
        if(stmt.type == 'uri'):
            stmt_node = URIRef(stmt.value)
        else:
            stmt_node = BNode() # a GUID is generated

        to_node = URIRef(to_uri.value)
        from_node = URIRef(from_uri.value)
        pred_node = URIRef(pred.value)
        linkset_node = URIRef(linksetInstance.value)

        g.add( (stmt_node, RDF.object, to_node) )
        g.add( (stmt_node, RDF.subject, from_node) )
        g.add( (stmt_node, RDF.predicate, pred_node) )
        g.add( (stmt_node, partOf, linkset_node) )
        g.add( (linkset_node, RDF.type, URIRef("http://linked.data.gov.au/def/loci#Linkset")) )

    return g


def get_triples():
    g1 = fetch_linked_data_ttl_from_source()
    g2 = fetch_linksets_from_cache()
    
    g1.serialize(destination="test_dataset.ttl", format='turtle')
    g2.serialize(destination="test_linkset.ttl", format='turtle')
    

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Generate Loc-I Test Data Triples From pylapi source')
    parser.add_argument('--verbose', dest='verbose', action='store_true',  help="Verbose mode. Include extra print outputs (default: off)")
    parser.add_argument('-o', '--outputfile', dest='outputfile', help='specify outputfile (default: print to stdout)')

    args = parser.parse_args()
    get_triples()

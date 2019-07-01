from SPARQLWrapper import SPARQLWrapper, JSON
import pytest


def query():
    sparql = SPARQLWrapper("http://13.238.155.4:7200/repositories/repo-test-1")
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT *
        WHERE { 
            ?x ?y ?z
        }
        LIMIT 10
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    print(results)   

def test_repo():
    query()
    testresults = ''
    assert testresults == testresults

def test_loci_count():
    """Test integrity of LOCI cache statement counts

    700754 statements for meshblocks
    
    TODO: GNAF, Geofabric, rest of ASGS ...
    TODO: Swap out to production SPARQL endpoint. Currently using http://13.238.155.4:7200/repositories/repo-test-1
    """
    sparql = SPARQLWrapper("http://13.238.155.4:7200/repositories/repo-test-1")
    sparql.setQuery("""
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX o: <http://www.w3.org/1999/02/22-rdf-syntax-ns#object>
        PREFIX p: <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate>
        PREFIX s: <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject>
        select  (count( ?stmt) as ?count)
        where { 
	        ?stmt dct:isPartOf <http://linked.data.gov.au/dataset/mb16cc> .
            ?stmt o: ?o .
            ?stmt p: ?p .
	        ?stmt s: ?s .
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)
    
    count_mb_stmt = results["results"]["bindings"][0]['count']['value']
    assert int(count_mb_stmt) == 700754    

   
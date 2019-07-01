from SPARQLWrapper import SPARQLWrapper, JSON

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
    
    
query()

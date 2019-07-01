from SPARQLWrapper import SPARQLWrapper, JSON
import json 

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
    
def query_type(loci_type):
    sparql = SPARQLWrapper("http://13.238.155.4:7200/repositories/repo-test-1")
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX loci: <http://linked.data.gov.au/def/loci#>
        select (count(distinct ?x) as ?count)
        where {{
            ?x a {definedtype}
        }}
    '''.format(definedtype=loci_type)
    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    count  = results["results"]["bindings"][0]['count']['value']
    #print(loci_type + ", " + count)
    return count
    
loci_types = [
    "<http://linked.data.gov.au/def/geofabric#ContractedCatchment>",
    "geo:Feature",
    "<http://linked.data.gov.au/def/geofabric#RiverRegion>",
    "loci:Linkset",
    "<http://linked.data.gov.au/def/asgs#MeshBlock>",
    "geo:Geometry",
    "<http://linked.data.gov.au/def/asgs#DestinationZone>",
    "<http://linked.data.gov.au/def/asgs#NaturalResourceManagementRegion>",
    "<http://linked.data.gov.au/def/asgs#StateSuburb>",
    "<http://linked.data.gov.au/def/asgs#StateOrTerritory>",
    "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1>",
    "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel2>",
    "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel3>",
    "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel4>",
    "<http://linked.data.gov.au/def/asgs#GreaterCapitalCityStatisticalArea>"
]

#query()

count_types = []
for curr in loci_types:
    count = query_type(curr)
    count_types.append((curr, count))

print(json.dumps(count_types, indent=4, sort_keys=True))

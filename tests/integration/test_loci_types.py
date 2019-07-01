import pytest
from SPARQLWrapper import SPARQLWrapper, JSON

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

testdata = [
    [
        "<http://linked.data.gov.au/def/geofabric#ContractedCatchment>",
        "30461"
    ],
    [
        "geo:Feature",
        "570372"
    ],
    [
        "<http://linked.data.gov.au/def/geofabric#RiverRegion>",
        "231"
    ],
    [
        "loci:Linkset",
        "4"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#MeshBlock>",
        "358007"
    ],
    [
        "geo:Geometry",
        "418217"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#DestinationZone>",
        "358007"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#NaturalResourceManagementRegion>",
        "358007"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StateSuburb>",
        "358007"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StateOrTerritory>",
        "8"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1>",
        "57489"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel2>",
        "2292"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel3>",
        "340"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#StatisticalAreaLevel4>",
        "89"
    ],
    [
        "<http://linked.data.gov.au/def/asgs#GreaterCapitalCityStatisticalArea>",
        "89"
    ]
]

@pytest.mark.parametrize("loci_type,count", testdata)
def test_loci_type_counts(loci_type, count):
    '''Test loci type counts

    '''
    currcount = query_type(loci_type)
    assert count == currcount
from SPARQLWrapper import SPARQLWrapper, JSON
from functools import reduce
import re

def query_type(loci_type, sparql_endpoint, auth=None):
    '''
        auth = expects a dict with 'user' and 'password' as keys with values,
              e.g. { 'user': 'username', 'password': 'passwordhere' }
    '''
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX loci: <http://linked.data.gov.au/def/loci#>
        PREFIX hyf: <https://www.opengis.net/def/appschema/hy_features/hyf/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
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

def query_sfWithin_mb_or_cc(locationUri, sparql_endpoint, auth=None):
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
        SELECT DISTINCT ?mb ?cc ?mbArea ?ccArea
        WHERE {{
            ?s dct:isPartOf <http://linked.data.gov.au/dataset/mb16cc> ;
            rdf:subject ?mb ;
            rdf:predicate geo:sfWithin ;
            rdf:object ?cc .
            ?mb a asgs:MeshBlock
            OPTIONAL {{
                ?mb geox:hasAreaM2 [ 
                        data:value ?mbArea ;
                        qb4st:crs epsg:3577
                    ] .
            }}
            OPTIONAL {{
                ?cc geox:hasAreaM2 [ 
                    data:value ?ccArea ;
                    qb4st:crs epsg:3577
                ] .                
            }}
            {filterStmt}
        }}
    '''.format(filterStmt=filterStmt)
    print(query)
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
                    'cc': res['cc']['value'], 
                    'mbArea': res['mbArea']['value'], 
                    'ccArea' : res['ccArea']['value']
                }
            )

    #do something    
    return withins_list


def query_sfWithin_mb_or_cc_with_graph(locationUri, sparql_endpoint, auth=None):
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
        SELECT DISTINCT ?mbOrIntersect ?cc ?pred ?mbArea ?ccArea ?mbAreaGraph ?ccAreaGraph
        WHERE {{
            ?s dct:isPartOf <http://linked.data.gov.au/dataset/mb16cc> ;
            rdf:subject ?mbOrIntersect ;
            rdf:predicate ?pred ;
            rdf:object ?cc .
            ?cc a <http://linked.data.gov.au/def/geofabric#ContractedCatchment>
            OPTIONAL {{
                ?mbOrIntersect geox:hasAreaM2 [ data:value ?mbArea ] .
            }}
            OPTIONAL {{
                ?cc geox:hasAreaM2 [ 
                    data:value ?ccArea ;
                ] .                
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

import json
def query_list_objects_sfContains_matching_loci_thing(loci_thing, loci_match_type, sparql_endpoint, auth=None):
    '''
        auth = expects a dict with 'user' and 'password' as keys with values,
              e.g. { 'user': 'username', 'password': 'passwordhere' }
    '''
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?o 
        WHERE {{ 
            {loci_subject} geo:sfContains+ ?o .
            ?o a {loci_type} .    
        }}
    '''.format(loci_subject=loci_thing, loci_type=loci_match_type)
    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #print(json.dumps(results, indent=4, sort_keys=True))

    matching_list = []
    for r in results["results"]["bindings"]:
        if 'o' in r:
            matching_list.append(r['o']['value'])

    #do something    
    return matching_list

def query_sfWithin(loci_thing, sparql_endpoint, auth=None):
    '''
        auth = expects a dict with 'user' and 'password' as keys with values,
              e.g. { 'user': 'username', 'password': 'passwordhere' }
    '''
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX dct: <http://purl.org/dc/terms/>
        select ?st ?link ?par
        where {{
            ?st dct:isPartOf ?lk ;
                rdf:subject {loci_subject} ;
                rdf:predicate geo:sfWithin ;
                rdf:object ?par .
        }}
    '''.format(loci_subject=loci_thing)
    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #print(json.dumps(results, indent=4, sort_keys=True))

    matching_list = []
    for r in results["results"]["bindings"]:
        if 'par' in r:
            matching_list.append(r['par']['value'])

    #do something    
    return matching_list

def count_type(loci_type, sparql_endpoint, auth=None):
    '''
        auth = expects a dict with 'user' and 'password' as keys with values,
              e.g. { 'user': 'username', 'password': 'passwordhere' }
    '''
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX loci: <http://linked.data.gov.au/def/loci#>
        PREFIX hyf: <https://www.opengis.net/def/appschema/hy_features/hyf/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
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

def query_intersecting_region_mb16cc(ccUri, mbUri,  sparql_endpoint, auth=None):
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX geox: <http://linked.data.gov.au/def/geox#>
        PREFIX data: <http://linked.data.gov.au/def/datatype/>
        PREFIX mb: <http://linked.data.gov.au/dataset/asgs2016/meshblock/>
        SELECT DISTINCT ?cc ?intersectionObj ?mb ?intersectingArea ?s1 ?s2
        WHERE {{
            ?s1 dct:isPartOf <http://linked.data.gov.au/dataset/mb16cc> ;
            rdf:subject ?cc ;
            rdf:predicate geo:sfContains ;
            rdf:object ?intersectionObj .
            ?s2 rdf:object ?intersectionObj .
            ?s2 rdf:predicate geo:sfContains .
            ?s2 rdf:subject ?mb .
            ?intersectionObj a geo:Feature
            OPTIONAL {{
                ?intersectionObj geox:hasAreaM2 [
                    data:value ?intersectingArea ;
                ] .               
                }}
            FILTER (?s1 != ?s2)
            FILTER (?cc = {contractedCatchmentUri})
            FILTER (?mb = {meshBlockUri} )
        }}
    '''.format(contractedCatchmentUri=ccUri, meshBlockUri=mbUri)
    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    res_list = []
    for res in results['results']['bindings']:
        res_list.append( {
                    'cc': res['cc']['value'], 
                    'intersectionObj' : res['intersectionObj']['value'], 
                    'mb': res['mb']['value'], 
                    'intersectingArea': res['intersectingArea']['value'], 
                    's1' : res['s1']['value'],
                    's2': res['s2']['value']                    
                }
            )
    return res_list

def query_mb16cc_contains(regionUri, sparql_endpoint, auth=None, verbose=True):
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])
    query = '''
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geox: <http://linked.data.gov.au/def/geox#>
        PREFIX data: <http://linked.data.gov.au/def/datatype/>
        PREFIX qb4st: <http://www.w3.org/ns/qb4st/>
        PREFIX epsg: <http://www.opengis.net/def/crs/EPSG/0/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        SELECT distinct ?from ?to ?fromAreaLinkset ?fromAreaDataset ?toAreaLinkset ?toAreaDataset ?toParent
        WHERE {{
            ?s dct:isPartOf ?ls ;
            rdf:subject ?from ;
            rdf:predicate geo:sfContains ;
            rdf:object ?to .
            OPTIONAL {{
                ?from geox:hasAreaM2 [
                    data:value ?fromAreaDataset ;
                    qb4st:crs epsg:3577
                ] .               
            }}
            OPTIONAL {{
                ?to geox:hasAreaM2 [
                    data:value ?toAreaLinkset ;
                    qb4st:crs epsg:3577;
                ] .     
            }}
            OPTIONAL {{ FILTER ((!sameTerm(?toParent,?from)) && (!sameTerm(?toParent,?to)))
                ?s1 dct:isPartOf ?ls ;
                    rdf:subject ?toParent ;
                    rdf:predicate geo:sfContains ;
                    rdf:object ?to .
            }}
            FILTER (!sameTerm(?from,?to))
            FILTER (?from = {regionUri})
            FILTER (?ls = <http://linked.data.gov.au/dataset/mb16cc>)
        }}'''.format(regionUri=regionUri)

    if verbose:
        print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    res_list = []
    for res in results['results']['bindings']:
        
        res_list.append( { #?from ?pred ?to ?fromArea ?toArea ?toParent
                    'from': res['from']['value']  if 'from' in res else None, 
                    'to': res['to']['value']  if 'to' in res else None, 
                    'fromAreaLinkset': res['fromAreaLinkset']['value'] if 'fromAreaLinkset' in res else None, 
                    'fromAreaDataset': res['fromAreaDataset']['value'] if 'fromAreaDataset' in res else None, 
                    'toAreaLinkset' : res['toAreaLinkset']['value'] if 'toAreaLinkset' in res else None ,
                    'toAreaDataset' : res['toAreaDataset']['value'] if 'toAreaDataset' in res else None ,
                    'toParent': res['toParent']['value'] if 'toParent' in res else None
                }
            )
    return res_list

def query_parent(uri, sparql_endpoint, auth=None, verbose=False):
    sparql = SPARQLWrapper(sparql_endpoint)
    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])
    query = '''
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geox: <http://linked.data.gov.au/def/geox#>
        PREFIX data: <http://linked.data.gov.au/def/datatype/>
        PREFIX qb4st: <http://www.w3.org/ns/qb4st/>
        PREFIX epsg: <http://www.opengis.net/def/crs/EPSG/0/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        SELECT ?sub (count(?mid) as ?distance) {{ 
        <{uri}> geo:sfWithin* ?mid .
        ?mid geo:sfWithin+ ?sub .
        }}
        group by ?sub 
        order by ?sub
        '''.format(uri=uri)

    if verbose:
        print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    res_list = []
    for res in results['results']['bindings']:
        res_list.append( { #?from ?pred ?to ?fromArea ?toArea ?toParent
                    'uri': res['sub']['value']  if 'sub' in res else None,
                    'distance': res['distance']['value']  if 'distance' in res else None 
                }
            )
    result = reduce((lambda x, y: x if x['distance'] > y['distance'] else y), res_list)
    return result['distance']

def query_rdftype(uri, sparql_endpoint, auth=None, verbose=False):
    sparql = SPARQLWrapper(sparql_endpoint)
    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])
    query = '''
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geox: <http://linked.data.gov.au/def/geox#>
        PREFIX data: <http://linked.data.gov.au/def/datatype/>
        PREFIX qb4st: <http://www.w3.org/ns/qb4st/>
        PREFIX epsg: <http://www.opengis.net/def/crs/EPSG/0/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        SELECT ?type 
        WHERE {{
            <{uri}> rdf:type ?type
        }}'''.format(uri=uri)

    if verbose:
        print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    res_list = []
    for res in results['results']['bindings']:
        res_list.append( { #?from ?pred ?to ?fromArea ?toArea ?toParent
                    'type': res['type']['value']  if 'type' in res else None, 
                }
            )
    return res_list

def query_mb16cc_contains_or_within(regionUri, sparql_endpoint, auth=None, verbose=False):
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])
    query = '''
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geox: <http://linked.data.gov.au/def/geox#>
        PREFIX data: <http://linked.data.gov.au/def/datatype/>
        PREFIX qb4st: <http://www.w3.org/ns/qb4st/>
        PREFIX epsg: <http://www.opengis.net/def/crs/EPSG/0/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        SELECT distinct ?from ?to ?fromAreaLinkset ?fromAreaDataset ?toAreaLinkset ?toAreaDataset ?toParent ?pred
        WHERE {{
            ?s dct:isPartOf ?ls ;
            rdf:subject ?from ;
            rdf:predicate ?pred ;
            rdf:object ?to .
            OPTIONAL {{
                ?from geox:hasAreaM2 [
                    data:value ?fromAreaLinkset ;
                    qb4st:crs epsg:3577
                ] .               
            }}
            OPTIONAL {{
                ?to geox:hasAreaM2 [
                    data:value ?toAreaLinkset ;
                    qb4st:crs epsg:3577;
                ] .     
            }}
            OPTIONAL {{ FILTER ((!sameTerm(?toParent,?from)) && (!sameTerm(?toParent,?to)))
                ?s1 dct:isPartOf ?ls ;
                    rdf:subject ?toParent ;
                    rdf:predicate geo:sfContains ;
                    rdf:object ?to .
            }}
            FILTER (!sameTerm(?from,?to))
            FILTER (?from = {regionUri})
            FILTER (?pred = geo:sfContains || ?pred = geo:sfWithin)
        }}'''.format(regionUri=regionUri)

    if verbose:
        print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    res_list = []
    for res in results['results']['bindings']:
        
        res_list.append( { #?from ?pred ?to ?fromArea ?toArea ?toParent
                    'from': res['from']['value']  if 'from' in res else None, 
                    'to': res['to']['value']  if 'to' in res else None, 
                    'fromAreaLinkset': res['fromAreaLinkset']['value'] if 'fromAreaLinkset' in res else None, 
                    'fromAreaDataset': res['fromAreaDataset']['value'] if 'fromAreaDataset' in res else None, 
                    'toAreaLinkset' : res['toAreaLinkset']['value'] if 'toAreaLinkset' in res else None ,
                    'toAreaDataset' : res['toAreaDataset']['value'] if 'toAreaDataset' in res else None ,
                    'toParent': res['toParent']['value'] if 'toParent' in res else None,
                    'pred': res['pred']['value'] if 'pred' in res else None
                }
            )
    return res_list

def query_mb16cc_relation(regionUri, sparql_endpoint, relationship="geo:sfContains", auth=None):
    '''Queries loci cache for mb16cc linkset relationships.

    Parameters
    ----------
    * regionUri: region used in the from field of the query
    * sparql_endpoint: which sparql endpoint to use
    * relationship: Which relationship/predicate to use (optional, default: geo:sfContains)
    * auth: authentication details, if needed (optional)
    '''

    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geox: <http://linked.data.gov.au/def/geox#>
        PREFIX data: <http://linked.data.gov.au/def/datatype/>
        PREFIX qb4st: <http://www.w3.org/ns/qb4st/>
        PREFIX epsg: <http://www.opengis.net/def/crs/EPSG/0/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        SELECT distinct ?from ?to ?fromAreaLinkset (min(?fromAreaLinkset) as ?fromAreaLinkset) (min(?toAreaLinkset) as ?toAreaLinkset) ?toParent 
        WHERE {{
            ?s dct:isPartOf ?ls ;
            rdf:subject ?from ;
            rdf:predicate {relationship} ;
            rdf:object ?to .
            OPTIONAL {{
                ?from geox:hasAreaM2 [
                    data:value ?fromAreaLinkset ;
                    qb4st:crs epsg:3577
                ] .               
            }}
            OPTIONAL {{
                ?to geox:hasAreaM2 [
                    data:value ?toAreaLinkset ;
                    qb4st:crs epsg:3577;
                ] .     
            }}
            OPTIONAL {{ FILTER ((!sameTerm(?toParent,?from)) && (!sameTerm(?toParent,?to)))
                ?s1 dct:isPartOf ?ls ;
                    rdf:subject ?toParent ;
                    rdf:predicate {relationship};
                    rdf:object ?to .
            }}
            FILTER (!sameTerm(?from,?to))
            FILTER (?from = {regionUri})
            FILTER (?ls = <http://linked.data.gov.au/dataset/mb16cc>)
        }} group by ?from ?s ?to ?toParent
        '''.format(regionUri=regionUri, relationship=relationship)

    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    res_list = []
    for res in results['results']['bindings']:
        
        res_list.append( { #?from ?pred ?to ?fromArea ?toArea ?toParent
                    'from': res['from']['value']  if 'from' in res else None, 
                    'to': res['to']['value']  if 'to' in res else None, 
                    'fromAreaLinkSet': res['fromAreaLinkSet']['value'] if 'fromAreaLinkSet' in res else None, 
                    'fromAreaDataset': res['fromAreaDataset']['value'] if 'fromAreaDataset' in res else None, 
                    'toAreaLinkset' : res['toAreaLinkset']['value'] if 'toAreaLinkset' in res else None ,
                    'toAreaDataset' : res['toAreaDataset']['value'] if 'toAreaDataset' in res else None ,
                    'toParent': res['toParent']['value'] if 'toParent' in res else None
                }
            )
    return res_list


def validate_uri_syntax(input_str):
    return bool(re.match(r"<http://.+>", input_str))

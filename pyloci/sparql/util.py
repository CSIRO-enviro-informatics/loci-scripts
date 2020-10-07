from SPARQLWrapper import SPARQLWrapper, JSON
from functools import reduce
import re



def list_type_instances_by_uristring(loci_type, loci_instance_prefix, sparql_endpoint, limit=100, offset=0, auth=None):
    '''
        Lists 
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
        select ?loci_instance
        where {{
            ?loci_instance a <{definedtype}> .
            FILTER( regex (str(?loci_instance), "^{loci_instance_prefix}"))

        }}
        ORDER BY (?loci_instance)
        LIMIT {limit}
        OFFSET {offset}
    '''.format(definedtype=loci_type, loci_instance_prefix=loci_instance_prefix, limit=limit, offset=offset)
    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #print(results)
    reslist = []
    for res in results["results"]["bindings"]:
        val = res['loci_instance']['value']
        if(val != None):
            reslist.append(val)
    #print(loci_type + ", " + count)
    return reslist

def list_type_instances(loci_type, sparql_endpoint, limit=100, offset=0, auth=None):
    '''
        Lists 
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
        select ?loci_instance
        where {{
            ?loci_instance a <{definedtype}>
        }}
        ORDER BY (?loci_instance)
        LIMIT {limit}
        OFFSET {offset}
    '''.format(definedtype=loci_type, limit=limit, offset=offset)
    #print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #print(results)
    reslist = []
    for res in results["results"]["bindings"]:
        val = res['loci_instance']['value']
        if(val != None):
            reslist.append(val)
    #print(loci_type + ", " + count)
    return reslist

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
                        geox:inCRS epsg:3577
                    ] .
            }}
            OPTIONAL {{
                ?cc geox:hasAreaM2 [ 
                    data:value ?ccArea ;
                    geox:inCRS epsg:3577
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
                    geox:inCRS epsg:3577
                ] .               
            }}
            OPTIONAL {{
                ?to geox:hasAreaM2 [
                    data:value ?toAreaLinkset ;
                    geox:inCRS epsg:3577;
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
                    geox:inCRS epsg:3577
                ] .               
            }}
            OPTIONAL {{
                ?to geox:hasAreaM2 [
                    data:value ?toAreaLinkset ;
                    geox:inCRS epsg:3577;
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
                    geox:inCRS epsg:3577
                ] .               
            }}
            OPTIONAL {{
                ?to geox:hasAreaM2 [
                    data:value ?toAreaLinkset ;
                    geox:inCRS epsg:3577;
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

def query_uri_id_mapping_table(featureTypeUri, idPropertyUri, sparql_endpoint, auth=None):
    '''Queries loci cache for <id, uri> mappings

    Parameters
    ----------
    * featureTypeUri: region used in the from field of the query
    * idPropertyUri: region used in the from field of the query
    * sparql_endpoint: which sparql endpoint to use
    * auth: authentication details, if needed (optional)
    '''
    
    sparql = SPARQLWrapper(sparql_endpoint)

    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])

    query = '''
        SELECT ?id ?lociUri WHERE {{
	        ?lociUri a {featureTypeUri} .
            ?lociUri {idPropertyUri} ?id .    
        }}
        orderby ?id
    '''.format(featureTypeUri=featureTypeUri, idPropertyUri=idPropertyUri)
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    res_list = []
    for res in results['results']['bindings']:                
        res_list.append( [ res['id']['value'], res['lociUri']['value'] ] )
    return res_list

def validate_uri_syntax(input_str):
    return bool(re.match(r"<http://.+>", input_str))

def iterate_query_for_labels_of_location(offset, limit, sparql_endpoint, auth=None, verbose=False):
    sparql = SPARQLWrapper(sparql_endpoint)
    if auth !=  None:
        sparql.setCredentials(user=auth['user'], passwd=auth['password'])
    query = '''
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX asgs: <http://linked.data.gov.au/def/asgs#> 
        PREFIX gnaf: <http://linked.data.gov.au/def/gnaf#> 
        PREFIX reg: <http://purl.org/linked-data/registry#>
        PREFIX dcterms: <http://purl.org/dc/terms/>

        SELECT DISTINCT ?l ?label
        WHERE {{
            {{ ?l a geo:Feature }}
            UNION
            {{
                ?c1 rdfs:subClassOf+ geo:Feature .
                ?l a ?c1 .
            }}
            UNION
            {{
                ?s1 rdf:subject ?l ;
                    rdf:predicate rdf:type ;
                    rdf:object geo:Feature .
            }}
            UNION
            {{ ?l a prov:Location }}
            UNION
            {{
                ?c2 rdfs:subClassOf+ prov:Location .
                ?l a ?c2 .
            }}
            UNION
            {{
                ?s2 rdf:subject ?l ;
                    rdf:predicate rdf:type ;
                    rdf:object prov:Location .
            }} .
            {{
                ?l asgs:mbCode2016 ?label
            }}
            UNION
            {{
                ?l asgs:sa2Name2016 ?label
            }}
            UNION
            {{
                ?l ?childCodeProp ?label .
                ?childCodeProp rdfs:subPropertyOf asgs:code
            }}
            UNION
            {{
                ?l ?childLabelProp ?label .
                ?childLabelProp rdfs:subPropertyOf asgs:label
            }}
            UNION
            {{
                ?l asgs:statisticalArea2Sa29DigitCode ?label
            }}            
            UNION
            {{
                ?l asgs:sa1Maincode2016 ?label
            }}            
            UNION
            {{
                ?l asgs:sa2Maincode2016 ?label
            }}            
            UNION
            {{
                ?l asgs:sa3Name2016 ?label
            }}
            UNION
            {{
                ?l asgs:sa3Code2016 ?label
            }}            
            UNION
            {{
                ?l asgs:sa4Name2016 ?label
            }}
            UNION
            {{
                ?l asgs:label  ?label
            }}
            UNION
            {{
                ?l asgs:stateName2016 ?label
            }}
            UNION
            {{
                ?l rdfs:label ?label
            }}
            UNION
            {{
                ?l  rdfs:comment ?label
            }}
            UNION
            {{
                ?l  gnaf:hasName ?label
            }}
            UNION
            {{
                ?l  dcterms:title  ?label
            }}
    		UNION
            {{
                ?l  dcterms:comment  ?label
            }}
    		UNION
    		{{
        		?l dcterms:identifier ?label
		    }}
            UNION
    		{{
		    	?l gnaf:hasAlias [ 
                    a gnaf:Alias ;
            		rdfs:label ?label
        		]    
    		}}
        }}
        OFFSET {offset}
        LIMIT {limit}
    '''.format(offset=offset, limit=limit)

    if verbose:
        print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    res_list = []
    for res in results['results']['bindings']:
        res_list.append( { #?from ?pred ?to ?fromArea ?toArea ?toParent
                    'location': res['l']['value']  if 'l' in res else None, 
                    'label': res['label']['value']  if 'label' in res else None, 
                }
            )
    return res_list

def query_labels_from_locations(sparql_endpoint, auth=None, verbose=False, offset=0, limit=1000000, max=None):
    count = 0
    curr_offset = offset
    #print from here
    
    while(True):
        res = iterate_query_for_labels_of_location(curr_offset, limit, sparql_endpoint, auth, verbose)
        res_count = len(res)
        if res_count > 0:
            for curr in res:
                if curr != None:
                    print('{location}\t{label}'.format(location=curr['location'], label=curr['label'])) 
                    count = count + 1
            curr_offset = curr_offset + res_count
        else:
            break

        if max != None and count > max:
            break

        
            



    
    
    
from SPARQLWrapper import SPARQLWrapper, JSON

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
    print(loci_type + ", " + count)
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
                ?mb geox:hasAreaM2 [ data:value ?mbArea ] .
            }}
            GRAPH <http://linked.data.gov.au/dataset/mb16cc> {{
                OPTIONAL {{
                    ?cc geox:hasAreaM2 [ 
                        data:value ?ccArea ;
                    ] .                
                }}
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
                    'cc': res['cc']['value'], 
                    'mbArea': res['mbArea']['value'], 
                    'ccArea' : res['ccArea']['value']
                }
            )

    #do something    
    return withins_list


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

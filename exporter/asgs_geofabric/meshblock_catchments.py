# -*- coding: utf-8 -*-
#
import psycopg2 as pg
import rdflib
from rdflib.namespace import Namespace, RDF, RDFS, XSD


GEO = Namespace("http://www.opengis.net/ont/geosparql#")
GEOX = Namespace("http://linked.data.gov.au/def/geox#")
DBP = Namespace("http://dbpedia.org/property/")
QUDT = Namespace("http://qudt.org/schema/qudt#")
PROV = Namespace("http://www.w3.org/ns/prov#")

Feature = GEO['Feature']
sfContains = GEO['sfContains']
sfWithin = GEO['sfWithin']
transitiveSfOverlap = GEOX['transitiveSfOverlap']
area = DBP['area']
unit = QUDT['unit']
numericValue = QUDT['numericValue']
sqm = QUDT['SquareMeter']
a = RDF['type']
decimalType = XSD['decimal']
doubleType = XSD['double']
r_subject = RDF['subject']
r_predicate = RDF['predicate']
r_object = RDF['object']
method = rdflib.URIRef("http://linked.data.gov.au/def/loci/hadGenerationMethod")
cc_pre = Namespace("http://linked.data.gov.au/dataset/geofabric/catchment/")
mb_pre = Namespace("http://linked.data.gov.au/dataset/asgs2016/meshblock/")

def mb_code_to_uri(code):
    #return rdflib.URIRef("http://linked.data.gov.au/dataset/asgs2016/meshblock/{}".format(str(code)))
    return mb_pre.term(str(code))

def cc_hydroid_to_uri(hydroid):
    #return rdflib.URIRef("http://linked.data.gov.au/dataset/geofabric/catchment/{}".format(str(hydroid)))
    return cc_pre.term(str(hydroid))


overlaps_template = """\
mb:{mb_code_2016:s} a f: ;
    dbp:area [ nv: {mb_area_m2:g} ;
            qudt:unit m2: ] .

cc:{hydroid:s} a f: ;
    dbp:area [ nv: {cc_area_m2:g} ;
            qudt:unit m2: ] .

:i{intersection_iter:d} a f: ;
    dbp:area [ nv: {i_area_m2:g} ;
            qudt:unit m2: ] .

:mo{intersection_iter:d} s: mb:{mb_code_2016:s} ;
    p: c: ;
    o: :i{intersection_iter:d} ;
    m: :proc .

:co{intersection_iter:d} s: cc:{hydroid:s} ;
    p: c: ;
    o: :i{intersection_iter:d} ;
    m: :proc .

:to{intersection_iter:d} s: mb:{mb_code_2016:s} ;
    p: tso: ;
    o: cc:{hydroid:s};
    m: :proc .

"""

mb_sf_within_template = """\
mw{within_iter:d}: s: mb:{mb_code_2016:s} ;
    p: w: ;
    o: cc:{hydroid:s} ;
    m: :proc .

"""

mb_sf_contains_template = """\
mw{within_iter:d}: s: mb:{mb_code_2016:s} ;
    p: c: ;
    o: cc:{hydroid:s} ;
    m: :proc .

"""


def populate_overlaps_template(**kwargs):
    return overlaps_template.format(**kwargs)


def main():
    g = rdflib.Graph()
    g.bind('', 'http://linked.data.gov.au/dataset/meshblockscatchments/')
    g.bind('geo', GEO)
    g.bind('geox', GEOX)
    g.bind('dbp', DBP)
    g.bind('qudt', QUDT)
    g.bind('prov', PROV)
    g.bind('sss', r_subject)
    g.bind('ppp', r_predicate)
    g.bind('ooo', r_object)
    g.bind('mmm', method)
    g.bind('www', sfWithin)
    g.bind('ccc', cc_pre)
    g.bind('mbb', mb_pre)


    plan_uri = rdflib.URIRef("http://linked.data.gov.au/dataset/meshblockscatchments/SpatialIntersection")
    g.add((plan_uri, a, PROV['Plan']))
    g.add((plan_uri, RDFS['label'], rdflib.Literal('Spatial Intersection Method')))
    g.add((plan_uri, RDFS['seeAlso'], rdflib.URIRef('https://todo.uriref.method.docs')))
    #g.bind('i', plan_uri)
    # todo: wasAttributedTo and generatedAtTime

    con = pg.connect("host=localhost dbname=intersect_me user=postgres password=password")
    cur = con.cursor("cur1")
    cur.execute("""
    SELECT mb.mb_code_2016, cc.hydroid, mb.mb_area, cc.cc_area, mb.i_area, mb.is_overlaps, cc.is_overlaps, mb.is_within, cc.is_within 
    FROM public."mbintersectccareas_classify" as mb
    INNER JOIN public."ccintersectmbareas_classify" as cc on mb.mb_code_2016 = cc.mb_code_2016 and mb.hydroid = cc.hydroid
    WHERE (mb.is_overlaps or cc.is_overlaps) and (not mb.is_within) and (not cc.is_within);
    --LIMIT 10;
    --ORDER BY mb.mb_code_2016;
    """)
    c = 0
    intersection_iter = 0
    with open("overlaps_all.ttl", "w") as outfile:
        for record in cur:
            intersection_iter += 1
            c+=1
            mb_code_2016 = str(record[0])
            #mb_uri = mb_code_to_uri(mb_code_2016)
            hydroid = str(record[1])
            #cc_uri = cc_hydroid_to_uri(hydroid)
            #g.add((mb_uri, a, Feature))
            #g.add((cc_uri, a, Feature))
            #mb_area = rdflib.BNode()
            #cc_area = rdflib.BNode()
            mb_area_m2 = float(record[2])
            cc_area_m2 = float(record[3])
            i_area_m2 = float(record[4])
            mb_area_m2 = round((mb_area_m2 / 100.0), 7) * 100.0
            cc_area_m2 = round((cc_area_m2 / 100.0), 7) * 100.0
            i_area_m2 = round((i_area_m2 / 100.0), 7) * 100.0

            # g.add((mb_area, numericValue, rdflib.Literal(mb_area_m2, datatype=doubleType)))
            # g.add((mb_area, unit, sqm))
            # g.add((mb_uri, area, mb_area))
            #
            # g.add((cc_area, numericValue, rdflib.Literal(cc_area_m2, datatype=doubleType)))
            # g.add((cc_area, unit, sqm))
            # g.add((cc_uri, area, cc_area))

            overlap = rdflib.BNode()
            g.add((overlap, a, Feature))
            overlap_area = rdflib.BNode()
            g.add((overlap_area, numericValue, rdflib.Literal(i_area_m2, datatype=doubleType)))
            g.add((overlap_area, unit, sqm))
            g.add((overlap, area, overlap_area))

            # g.add((mb_uri, sfContains, overlap))
            assertion_b1 = rdflib.BNode()
            g.add((assertion_b1, r_subject, mb_uri))
            g.add((assertion_b1, r_predicate, sfContains))
            g.add((assertion_b1, r_object, overlap))
            g.add((assertion_b1, method, plan_uri))

            # g.add((cc_uri, sfContains, overlap))
            assertion_b2 = rdflib.BNode()
            g.add((assertion_b2, r_subject, cc_uri))
            g.add((assertion_b2, r_predicate, sfContains))
            g.add((assertion_b2, r_object, overlap))
            g.add((assertion_b2, method, plan_uri))

            assertion_b3 = rdflib.BNode()
            # g.add((mb_uri, transitiveSfOverlap, cc_uri))
            g.add((assertion_b3, r_subject, mb_uri))
            g.add((assertion_b3, r_predicate, transitiveSfOverlap))
            g.add((assertion_b3, r_object, cc_uri))
            g.add((assertion_b3, method, plan_uri))

            next_chunk = overlaps_template.format(mb_code_2016=mb_code_2016, hydroid=hydroid, intersection_iter=intersection_iter, mb_area_m2=mb_area_m2, cc_area_m2=cc_area_m2, i_area_m2=i_area_m2)
            outfile.write(next_chunk)
    # with open("overlaps.ttl", 'wb') as f:
    #     g.serialize(destination=f, format='turtle')

def main2():
    # g = rdflib.Graph()
    # g.bind('geo', GEO)
    # g.bind('geox', GEOX)
    # g.bind('dbp', DBP)
    # g.bind('qudt', QUDT)
    con = pg.connect("host=localhost dbname=intersect_me user=postgres password=password")

    cur = con.cursor("cur2")
    cur.execute("""
    SELECT mb.mb_code_2016, cc.hydroid, mb.is_within, cc.is_within 
    FROM public."mbintersectccareas_classify" as mb
    INNER JOIN public."ccintersectmbareas_classify" as cc on mb.mb_code_2016 = cc.mb_code_2016 and mb.hydroid = cc.hydroid
    WHERE mb.is_within or cc.is_within;
    --LIMIT 10;
    --ORDER BY mb.mb_code_2016;
    """)
    c = 0
    within_iter = 0
    with open("within_all.ttl", "w") as outfile:
        for record in cur:
            c+=1
            within_iter += 1
            mb_code_2016 = str(record[0])
            # mb_uri = mb_code_to_uri(mb_code_2016)
            hydroid = str(record[1])
            mb_is_within = bool(record[2])
            cc_is_within = bool(record[3])
            if mb_is_within:
                next_chunk = mb_sf_within_template.format(mb_code_2016=mb_code_2016, hydroid=hydroid, within_iter=within_iter)
            else:
                next_chunk = mb_sf_contains_template.format(mb_code_2016=mb_code_2016, hydroid=hydroid, within_iter=within_iter)

            # cc_uri = cc_hydroid_to_uri(hydroid)
            #g.add((mb_uri, a, Feature))
            #g.add((cc_uri, a, Feature))

            #break
            outfile.write(next_chunk)
    # print(c)
    # with open("overlaps.ttl", 'wb') as f:
    #     g.serialize(destination=f, format='turtle')

if __name__ == "__main__":
    #main()
    main2()

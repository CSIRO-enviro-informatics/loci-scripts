# -*- coding: utf-8 -*-
#
from pyldapi_client import LDAPIClient
from exporter.helpers import chunks, ld_find_subject
import pickle
import re
import xlsxwriter

LDAPI_CLIENT_REMAPPER = {
    "http://linked.data.gov.au/dataset/gnaf": "http://localhost:5000",
    "http://gnafld.net": "http://localhost:5000",
}

HEADERS = (
    'identifier',
    'class',
)

gnaf_gnafType = "http://linked.data.gov.au/def/gnaf#gnafType"
gnaf_hasState = "http://linked.data.gov.au/def/gnaf#hasState"
gnaf_hasLocality = "http://linked.data.gov.au/def/gnaf#hasLocality"
geos_hasGeometry = "http://www.opengis.net/ont/geosparql#hasGeometry"
geos_asWKT = "http://www.opengis.net/ont/geosparql#asWKT"
latlng_wkt_regex = re.compile(r'.*POINT\s*\(([^\s]+)\s+([^\s]+)\)', flags=re.IGNORECASE)


class GNAFFeatureExporter(object):

    def write_worksheet_header(self, worksheet):
        """
        :param worksheet:
        :type worksheet: xlsxwriter.writer.Worksheet
        :return:
        """
        headers = list(HEADERS)
        if self.register_end == "address":
            headers.append("type")
            headers.append("text")
            headers.append("state")
            headers.append("locality")
            headers.append("lat")
            headers.append("lng")
        elif self.register_end == "locality":
            headers.append("state")
        i = 0
        for i, h in enumerate(headers):
            worksheet._write_string(0, i, h)
            worksheet.set_column(i, i, 30)

    def write_csv_header(self, csv_file):
        """
        :param csv_file:
        :type csv_file: IO
        :return:
        """
        headers = list(HEADERS)
        if self.register_end == "address":
            headers.append("type")
            headers.append("text")
            headers.append("state")
            headers.append("locality")
            headers.append("lat")
            headers.append("lng")
        elif self.register_end == "locality":
            headers.append("state")
        for h in headers[0:-1]:
            csv_file.write("{},".format(h))
        csv_file.write("{}\n".format(headers[-1]))

    def write_worksheet_url(self, worksheet, row, col, url, text):
        if self.url_count > 65500:
            worksheet._write_string(row, col, str(url))
        else:
            worksheet.write_url(row, col, str(url), string=str(text))
            self.url_count += 1

    def write_worksheet_item(self, worksheet, i, identifier, class_uri, has_type=None, has_text=None, has_state=None, has_locality=None, has_coord=None):
        row = i+1
        identifier_text = identifier.rsplit('/', 1)[-1]
        self.write_worksheet_url(worksheet, row, 0, identifier, identifier_text)
        class_text = class_uri.rsplit('/', 1)[-1]
        self.write_worksheet_url(worksheet, row, 1, class_uri, class_text)
        is_address = self.register_end == "address"
        is_locality = self.register_end == "locality"
        col = 2
        if is_address:
            if has_type:
                has_type_text = has_type.rsplit('/', 1)[-1]
                self.write_worksheet_url(worksheet, row, col, has_type, has_type_text)
            col += 1
            if has_text:
                worksheet._write_string(row, col, str(has_text))
            col += 1
        if is_locality or is_address:
            if has_state:
                has_state_text = has_state.rsplit('/', 1)[-1]
                self.write_worksheet_url(worksheet, row, col, has_state, has_state_text)
            col += 1
        if is_address:
            if has_locality:
                has_loc_text = has_locality.rsplit('/', 1)[-1]
                self.write_worksheet_url(worksheet, row, col, has_locality, has_loc_text)
            col += 1
            if has_coord:
                worksheet._write_string(row, col, str(has_coord[0]))
                worksheet._write_string(row, col+1, str(has_coord[1]))
            col += 2

    def write_csv_item(self, csv_file, identifier, class_uri, has_type=None, has_text=None, has_state=None, has_locality=None, has_coord=None):
        csv_file.write("{},".format(str(identifier)))
        csv_file.write("{}".format(str(class_uri)))
        is_address = self.register_end == "address"
        is_locality = self.register_end == "locality"
        if is_address:
            if has_type:
                csv_file.write(",{}".format(str(has_type)))
            else:
                csv_file.write(",")
            if has_text:
                cleaned_text = str(has_text).replace("\"", "&quot;")
                csv_file.write(",\"{}\"".format(cleaned_text))
            else:
                csv_file.write(",")
        if is_locality or is_address:
            if has_state:
                csv_file.write(",{}".format(str(has_state)))
            else:
                csv_file.write(",")
        if is_address:
            if has_locality:
                csv_file.write(",{}".format(str(has_locality)))
            else:
                csv_file.write(",")
            if has_coord:
                csv_file.write(",{},{}\n".format(str(has_coord[0]), str(has_coord[1])))
            else:
                csv_file.write(",,\n")
        else:
            csv_file.write("\n")

    def export_csv_index(self, csv_file, index, limit=None):
        for i, (k, v) in enumerate(index.items()):
            try:
                identifier = str(v['@id'])
                class_name = str(v['@type'][0])
            except (KeyError, AttributeError) as e:
                print("Issue with index id: {}".format(str(k)))
                raise e
            self.write_csv_item(csv_file, identifier, class_name)
            if limit is not None and i >= limit:
                break

    def export_xlsx_index(self, worksheet, index, limit=None):
        for i, (k, v) in enumerate(index.items()):
            try:
                identifier = str(v['@id'])
                class_name = str(v['@type'][0])
            except (KeyError, AttributeError) as e:
                print("Issue with index id: {}".format(str(k)))
                raise e
            self.write_worksheet_item(worksheet, i, identifier, class_name)
            if limit is not None and i >= limit:
                break

    def export_xlsx_all(self, worksheet, index, limit=None):
        if isinstance(index, dict):
            index = tuple(index.keys())
        if limit is not None:
            limit = int(limit)
            assert limit > 0
            index = index[0:limit]
        for j, sixteen in enumerate(chunks(index, 16)):
            instances = self.register.instances(index=sixteen)
            for i, (instance_id, resource) in enumerate(instances.items()):
                d = ld_find_subject(resource, instance_id)
                if d is None:
                    continue
                identifier = str(d['@id'])
                class_name = str(sorted(d['@type'])[0])
                try:
                    has_type = d[gnaf_gnafType]
                    has_type = [w['@id'] for w in has_type]
                    has_type = sorted(has_type)[0]
                except (KeyError, IndexError, AttributeError):
                    has_type = None
                except Exception as e:
                    raise e
                try:
                    has_text = d["http://www.w3.org/2000/01/rdf-schema#comment"]
                    has_text = [w['@value'] for w in has_text]
                    has_text = sorted(has_text)[0]
                except (KeyError, IndexError, AttributeError):
                    has_text = None
                try:
                    has_state = d[gnaf_hasState]
                    has_state = [w['@id'] for w in has_state]
                    has_state = sorted(has_state)[0]
                except (KeyError, IndexError, AttributeError):
                    has_state = None
                except Exception as e:
                    raise e
                try:
                    has_locality = d[gnaf_hasLocality]
                    has_locality = [w['@id'] for w in has_locality]
                    has_locality = sorted(has_locality)[0]
                except (KeyError, IndexError, AttributeError):
                    has_locality = None
                try:
                    has_geometry = d[geos_hasGeometry]
                    has_geometry = [w['@id'] for w in has_geometry]
                    has_geometry = sorted(has_geometry)[0]
                    geo_obj = ld_find_subject(resource, has_geometry)
                    assert geo_obj and isinstance(geo_obj, dict)
                    as_wkt = geo_obj[geos_asWKT]
                    as_wkt = [w['@value'] for w in as_wkt]
                    as_wkt = sorted(as_wkt)[0]
                    found = latlng_wkt_regex.search(as_wkt)
                    assert found
                    lng = found[1]
                    lat = found[2]
                    has_coord = (lat, lng)
                except (KeyError, IndexError, AttributeError, AssertionError):
                    has_coord = None
                except Exception as e:
                    raise e
                self.write_worksheet_item(worksheet, (j*16)+i, identifier, class_name, has_type, has_text, has_state, has_locality, has_coord)

    def export_csv_all(self, csv_file, index, limit=None):
        if isinstance(index, dict):
            index = tuple(index.keys())
        if limit is not None:
            limit = int(limit)
            assert limit > 0
            index = index[0:limit]
        for j, sixteen in enumerate(chunks(index, 16)):
            instances = self.register.instances(index=sixteen)
            for i, (instance_id, resource) in enumerate(instances.items()):
                d = ld_find_subject(resource, instance_id)
                if d is None:
                    continue
                identifier = str(d['@id'])
                class_name = str(sorted(d['@type'])[0])
                try:
                    has_type = d[gnaf_gnafType]
                    has_type = [w['@id'] for w in has_type]
                    has_type = sorted(has_type)[0]
                except (KeyError, IndexError, AttributeError):
                    has_type = None
                except Exception as e:
                    raise e
                try:
                    has_text = d["http://www.w3.org/2000/01/rdf-schema#comment"]
                    has_text = [w['@value'] for w in has_text]
                    has_text = sorted(has_text)[0]
                except (KeyError, IndexError, AttributeError):
                    has_text = None
                try:
                    has_state = d[gnaf_hasState]
                    has_state = [w['@id'] for w in has_state]
                    has_state = sorted(has_state)[0]
                except (KeyError, IndexError, AttributeError):
                    has_state = None
                except Exception as e:
                    raise e
                try:
                    has_locality = d[gnaf_hasLocality]
                    has_locality = [w['@id'] for w in has_locality]
                    has_locality = sorted(has_locality)[0]
                except (KeyError, IndexError, AttributeError):
                    has_locality = None
                except Exception as e:
                    raise e
                try:
                    has_geometry = d[geos_hasGeometry]
                    has_geometry = [w['@id'] for w in has_geometry]
                    has_geometry = sorted(has_geometry)[0]
                    geo_obj = ld_find_subject(resource, has_geometry)
                    assert geo_obj and isinstance(geo_obj, dict)
                    as_wkt = geo_obj[geos_asWKT]
                    as_wkt = [w['@value'] for w in as_wkt]
                    as_wkt = sorted(as_wkt)[0]
                    found = latlng_wkt_regex.search(as_wkt)
                    assert found
                    lng = found[1]
                    lat = found[2]
                    has_coord = (lat, lng)
                except (KeyError, IndexError, AttributeError, AssertionError):
                    has_coord = None
                except Exception as e:
                    raise e
                self.write_csv_item(csv_file, identifier, class_name, has_type, has_text, has_state, has_locality, has_coord)

    def _export_as_xlsx(self, *args, limit=None, **kwargs):
        suffix = self.register_end
        #reset to first page, and increase per_page
        _ = self.register.index_page(page=1, per_page=100)
        pickle_filename = "{}_index_{}.pickle".format(suffix, str(limit))
        try:
            with open(pickle_filename, 'rb') as f:
                index = pickle.load(f)
        except:
            index = self.register.index(min_count=limit)
            with open(pickle_filename, 'wb') as f:
                pickle.dump(index, f)
        dont_close_workbook = False
        if 'workbook' in kwargs:
            workbook = kwargs.pop('workbook')
            dont_close_workbook = True
        else:
            workbook = xlsxwriter.Workbook('gnaf_{}.xlsx'.format(suffix))
        worksheet = workbook.add_worksheet()
        if 'worksheet_name' in kwargs:
            name = kwargs.pop('worksheet_name')
            worksheet.name = name
        self.write_worksheet_header(worksheet)
        if self.just_index:
            self.export_xlsx_index(worksheet, index, limit=limit)
        else:
            self.export_xlsx_all(worksheet, index, limit=limit)
        if not dont_close_workbook:
            workbook.close()

    def _export_as_csv(self, *args, limit=None, **kwargs):
        suffix = self.register_end
        #reset to first page, and increase per_page
        _ = self.register.index_page(page=1, per_page=100)
        pickle_filename = "{}_index_{}.pickle".format(suffix, str(limit))
        try:
            with open(pickle_filename, 'rb') as f:
                index = pickle.load(f)
        except:
            index = self.register.index(min_count=limit)
            with open(pickle_filename, 'wb') as f:
                pickle.dump(index, f)
        file = open("gnaf_{}.csv".format(suffix), 'w', encoding='utf-8')
        try:
            self.write_csv_header(file)
            if self.just_index:
                self.export_csv_index(file, index, limit=limit)
            else:
                self.export_csv_all(file, index, limit=limit)
        finally:
            file.close()

    def export(self, *args, mode="excel", **kwargs):
        if mode == "excel" or mode == "xlsx":
            return self._export_as_xlsx(*args, **kwargs)
        elif mode == "csv":
            return self._export_as_csv(*args, **kwargs)
        else:
            raise NotImplementedError(
                "No exporter mode \"{}\"".format(mode))

    def __init__(self, just_index=False, register_end="locality"):
        self.url_count = 0
        self.just_index = just_index
        self.register_end = register_end
        self.client = LDAPIClient(
            "http://linked.data.gov.au/dataset/gnaf",
            url_remapper=LDAPI_CLIENT_REMAPPER
        )
        self.register = self.client.register("http://linked.data.gov.au/dataset/gnaf/{}/".format(self.register_end))

if __name__ == "__main__":
    e = GNAFFeatureExporter(just_index=False, register_end="address")
    e.export(limit=3000, mode="csv")


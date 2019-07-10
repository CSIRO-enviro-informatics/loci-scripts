# -*- coding: utf-8 -*-
#
from pyldapi_client import LDAPIClient
from exporter.helpers import chunks, ld_find_subject
import pickle
import xlsxwriter

LDAPI_CLIENT_REMAPPER = {
    "http://test.linked.data.gov.au/dataset/geofabric": "http://localhost:5001",
    "http://geofabricld.net": "http://localhost:5001",
}

HEADERS = (
    'identifier',
    'class',
)

hyf_lower = "https://www.opengis.net/def/appschema/hy_features/hyf/lowerCatchment"
geo_sfwithin = "http://www.opengis.net/ont/geosparql#sfWithin"

class GeofabricFeatureExporter(object):

    def write_worksheet_header(self, worksheet):
        """
        :param worksheet:
        :type worksheet: xlsxwriter.writer.Worksheet
        :return:
        """
        i = 0
        for i, h in enumerate(HEADERS):
            worksheet._write_string(0, i, h)
        worksheet.set_column(0, 0, 36)
        worksheet.set_column(1, 1, 36)
        if self.register_end == "catchment":
            worksheet._write_string(0, i+1, "riverRegion")
            worksheet.set_column(2, 2, 36)
            worksheet._write_string(0, i+2, "drainageDivision")
            worksheet.set_column(2, 3, 36)

    def write_csv_header(self, csv_file):
        """
        :param csv_file:
        :type csv_file: IO
        :return:
        """
        headers = list(HEADERS)
        if self.register_end == "catchment":
            headers.append("riverRegion")
            headers.append("drainageDivision")
        for h in headers[0:-1]:
            csv_file.write("{},".format(h))
        csv_file.write("{}\n".format(headers[-1]))

    def write_worksheet_url(self, worksheet, row, col, url, text):
        if self.url_count > 65500:
            worksheet._write_string(row, col, str(url))
        else:
            worksheet.write_url(row, col, str(url), string=str(text))
            self.url_count += 1

    def write_worksheet_item(self, worksheet, i, identifier, class_uri, has_rr=None, has_dd=None):
        identifier_text = identifier.rsplit('/', 1)[-1]
        row = i+1
        self.write_worksheet_url(worksheet, row, 0, identifier, identifier_text)
        class_text = class_uri.rsplit('/', 1)[-1]
        self.write_worksheet_url(worksheet, row, 1, class_uri, class_text)
        if self.register_end == "catchment":
            if has_rr:
                has_rr_text = has_rr.rsplit('/', 1)[-1]
                self.write_worksheet_url(worksheet, row, 2, has_rr, has_rr_text)
            if has_dd:
                has_dd_text = has_dd.rsplit('/', 1)[-1]
                self.write_worksheet_url(worksheet, row, 3, has_dd, has_dd_text)

    def write_csv_item(self, csv_file, identifier, class_uri, has_rr=None, has_dd=None):
        csv_file.write("{},".format(str(identifier)))
        csv_file.write("{}".format(str(class_uri)))
        if self.register_end == "catchment":
            if has_rr:
                csv_file.write(",{}".format(str(has_rr)))
            else:
                csv_file.write(",")
            if has_dd:
                csv_file.write(",{}\n".format(str(has_dd)))
            else:
                csv_file.write(",\n")
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
                    has_within = d[geo_sfwithin]
                    has_within = [w['@id'] for w in has_within]
                    has_rr = None
                    has_dd = None
                    for w in has_within:
                        if "/riverregion/" in w:
                            has_rr = str(w)
                        elif "/drainagedivision/" in w:
                            has_dd = str(w)
                except (KeyError, IndexError, AttributeError):
                    has_rr = None
                    has_dd = None
                except Exception as e:
                    raise e
                self.write_worksheet_item(worksheet, (j*16)+i, identifier, class_name, has_rr, has_dd)

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
                    has_within = d[geo_sfwithin]
                    has_within = [w['@id'] for w in has_within]
                    has_rr = None
                    has_dd = None
                    for w in has_within:
                        if "/riverregion/" in w:
                            has_rr = str(w)
                        elif "/drainagedivision/" in w:
                            has_dd = str(w)
                except (KeyError, IndexError, AttributeError):
                    has_rr = None
                    has_dd = None
                self.write_csv_item(csv_file, identifier, class_name, has_rr, has_dd)

    def _export_as_xlsx(self, *args, limit=None, **kwargs):
        suffix = self.register_end
        #reset to first page, and increase per_page
        _ = self.register.index_page(page=1, per_page=100)
        pickle_filename = "{}_index_{}.pickle".format(suffix, str(limit))
        try:
            with open(pickle_filename, 'rb') as f:
                index = pickle.load(f)
        except FileNotFoundError:
            index = self.register.index(offset=28000, min_count=limit)
            with open(pickle_filename, 'wb') as f:
                pickle.dump(index, f)
        dont_close_workbook = False
        if 'workbook' in kwargs:
            workbook = kwargs.pop('workbook')
            dont_close_workbook = True
        else:
            workbook = xlsxwriter.Workbook('geofabric_{}.xlsx'.format(suffix))
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
        pickle_filename = "{}_index_{}.pickle".format(suffix, str(limit))
        try:
            with open(pickle_filename, 'rb') as f:
                index = pickle.load(f)
        except:
            index = self.register.index(offset=28000, min_count=limit)
            with open(pickle_filename, 'wb') as f:
                pickle.dump(index, f)
        file = open("geofabric_{}.csv".format(suffix), 'w', encoding='utf-8')
        try:
            self.write_csv_header(file)
            if self.just_index:
                self.export_csv_index(file, index, limit=limit)
            else:
                self.export_csv_all(file, index, limit=limit)
        finally:
            file.close()

    def export(self, *args, mode='csv', **kwargs):
        if mode == "excel" or mode == "xlsx":
            return self._export_as_xlsx(*args, **kwargs)
        elif mode == "csv":
            return self._export_as_csv(*args, **kwargs)
        else:
            raise NotImplementedError(
                "No exporter mode \"{}\"".format(mode))

    def __init__(self, just_index=False, register_end="catchment",):
        self.url_count = 0
        self.just_index = just_index
        self.register_end = register_end
        self.client = LDAPIClient(
            "http://geofabricld.net",
            url_remapper=LDAPI_CLIENT_REMAPPER
        )
        self.register = self.client.register("http://geofabricld.net/{}/".format(self.register_end))

def main():
    e = GeofabricFeatureExporter(just_index=False, register_end="catchment")
    e.export(limit=3000, mode="csv")


def main_multisheet_workbook():
    workbook = xlsxwriter.Workbook('geof_test2.xlsx')
    e2 = GeofabricFeatureExporter(just_index=False, register_end="catchment")
    e2.export(limit=3000, workbook=workbook, worksheet_name="Catchment", mode="excel")
    e2 = GeofabricFeatureExporter(just_index=False, register_end="riverregion")
    e2.export(workbook=workbook, worksheet_name="RiverRegion", mode="excel")  # 218
    e2 = GeofabricFeatureExporter(just_index=False, register_end="drainagedivision")
    e2.export(workbook=workbook, worksheet_name="DrainageDivision", mode="excel")  # 13
    workbook.close()


if __name__ == "__main__":
    main()
    #main_multisheet_workbook()

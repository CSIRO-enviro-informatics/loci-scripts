# -*- coding: utf-8 -*-
#
from pyldapi_client import LDAPIClient
from exporter.helpers import chunks, ld_find_subject, ld_find_as_object
import pickle
import xlsxwriter

LDAPI_CLIENT_REMAPPER = {
    "http://linked.data.gov.au/dataset/asgs2016": "http://localhost:5000"
}

HEADERS = (
    'Identifier',
    'Class'
)

class ASGSFeatureExporter(object):

    def write_worksheet_header(self, worksheet):
        """
        :param worksheet:
        :type worksheet: xlsxwriter.writer.Worksheet
        :return:
        """
        headers = list(HEADERS)
        if self.register_end == "meshblock":
            headers.append("State")
            headers.append("Within SA1")
        elif self.register_end == "statisticalarealevel1":
            headers.append("State")
            headers.append("Within SA2")
        elif self.register_end == "statisticalarealevel2":
            headers.append("State")
            headers.append("Within SA3")
        elif self.register_end == "statisticalarealevel3":
            headers.append("State")
            headers.append("Within SA4")
        elif self.register_end == "statisticalarealevel4":
            headers.append("State")
        for i, h in enumerate(headers):
            worksheet._write_string(0, i, h)
            worksheet.set_column(i, i, 20)

    def write_csv_header(self, csv_file):
        """
        :param csv_file:
        :type csv_file: IO
        :return:
        """
        headers = list(HEADERS)
        if self.register_end == "meshblock":
            headers.append("State")
            headers.append("Within_sa1")
        elif self.register_end == "statisticalarealevel1":
            headers.append("State")
            headers.append("Within_sa2")
        elif self.register_end == "statisticalarealevel2":
            headers.append("State")
            headers.append("Within_sa3")
        elif self.register_end == "statisticalarealevel3":
            headers.append("State")
            headers.append("Within_sa4")
        elif self.register_end == "statisticalarealevel4":
            headers.append("State")
        for h in headers[0:-1]:
            csv_file.write("{},".format(h))
        csv_file.write("{}\n".format(headers[-1]))

    def write_worksheet_url(self, worksheet, row, col, url, text):
        if self.url_count > 65500:
            worksheet._write_string(row, col, str(url))
        else:
            worksheet.write_url(row, col, str(url), string=str(text))
            self.url_count += 1

    def write_worksheet_item(self, worksheet, i, identifier, class_uri, has_state=None, has_within=None):
        identifier_text = identifier.rsplit('/', 1)[-1]
        self.write_worksheet_url(worksheet, i + 1, 0, identifier, identifier_text)
        class_text = class_uri.rsplit('/', 1)[-1]
        self.write_worksheet_url(worksheet, i + 1, 1, class_uri, class_text)
        if has_state:
            has_state_text = has_state.rsplit('/', 1)[-1]
            self.write_worksheet_url(worksheet, i + 1, 2, has_state, has_state_text)
        if has_within:
            has_within_text = has_within.rsplit('/', 1)[-1]
            self.write_worksheet_url(worksheet, i + 1, 3, has_within, has_within_text)

    def write_csv_item(self, csv_file, identifier, class_uri, has_state=None, has_within=None):
        csv_file.write("{},".format(str(identifier)))
        csv_file.write("{},".format(str(class_uri)))
        if has_state:
            csv_file.write("{},".format(str(has_state)))
        else:
            csv_file.write(",")
        if has_within:
            csv_file.write("{}\n".format(str(has_within)))
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
        for j, chunk in enumerate(chunks(index, 16)):
            instances = self.register.instances(index=chunk)
            for i, (instance_id, resource) in enumerate(instances.items()):
                d = ld_find_subject(resource, instance_id)
                if d is None:
                    continue
                identifier = str(d['@id'])
                class_name = str(sorted(d['@type'])[0])
                has_state = None
                has_within = None
                inverses = ld_find_as_object(resource, instance_id)
                for inv in inverses:
                    subj, pred = inv
                    if pred == "http://linked.data.gov.au/def/asgs#isStateOrTerritoryOf":
                        has_state = subj
                    elif class_name == "http://linked.data.gov.au/def/asgs#MeshBlock" and pred == "http://linked.data.gov.au/def/asgs#isStatisticalAreaLevel1Of":
                        has_within = subj
                    elif class_name == "http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1" and pred == "http://linked.data.gov.au/def/asgs#isStatisticalAreaLevel2Of":
                        has_within = subj
                    elif class_name == "http://linked.data.gov.au/def/asgs#StatisticalAreaLevel2" and pred == "http://linked.data.gov.au/def/asgs#isStatisticalAreaLevel3Of":
                        has_within = subj
                    elif class_name == "http://linked.data.gov.au/def/asgs#StatisticalAreaLevel3" and pred == "http://linked.data.gov.au/def/asgs#isStatisticalAreaLevel4Of":
                        has_within = subj
                self.write_worksheet_item(worksheet, (j*16)+i, identifier, class_name, has_state, has_within)

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
                has_state = None
                has_within = None
                inverses = ld_find_as_object(resource, instance_id)
                for inv in inverses:
                    subj, pred = inv
                    if pred == "http://linked.data.gov.au/def/asgs#isStateOrTerritoryOf":
                        has_state = subj
                    elif class_name == "http://linked.data.gov.au/def/asgs#MeshBlock" and pred == "http://linked.data.gov.au/def/asgs#isStatisticalAreaLevel1Of":
                        has_within = subj
                    elif class_name == "http://linked.data.gov.au/def/asgs#StatisticalAreaLevel1" and pred == "http://linked.data.gov.au/def/asgs#isStatisticalAreaLevel2Of":
                        has_within = subj
                    elif class_name == "http://linked.data.gov.au/def/asgs#StatisticalAreaLevel2" and pred == "http://linked.data.gov.au/def/asgs#isStatisticalAreaLevel3Of":
                        has_within = subj
                    elif class_name == "http://linked.data.gov.au/def/asgs#StatisticalAreaLevel3" and pred == "http://linked.data.gov.au/def/asgs#isStatisticalAreaLevel4Of":
                        has_within = subj
                self.write_csv_item(csv_file, identifier, class_name, has_state, has_within)

    def _export_as_xlsx(self, *args, limit=None, **kwargs):
        suffix = self.register_end
        register = self.register
        pickle_filename = "{}_index_{}.pickle".format(suffix, limit)
        try:
            with open(pickle_filename, 'rb') as f:
                index = pickle.load(f)
        except FileNotFoundError:
            index = register.index(min_count=limit)
            with open(pickle_filename, 'wb') as f:
                pickle.dump(index, f)
        dont_close_workbook = False
        if 'workbook' in kwargs:
            workbook = kwargs.pop('workbook')
            dont_close_workbook = True
        else:
            workbook = xlsxwriter.Workbook('asgs_{}.xlsx'.format(suffix))
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
        #index = register.index()
        register = self.register
        try:
            with open("{}_index_{}.pickle".format(suffix, limit), 'rb') as f:
                index = pickle.load(f)
        except FileNotFoundError:
            index = register.index(min_count=limit)
            with open("{}_index_{}.pickle".format(suffix, limit), 'wb') as f:
                pickle.dump(index, f)
        file = open("asgs_{}.csv".format(suffix), 'w', encoding='utf-8')
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

    def __init__(self, just_index=False, register_end="statisticalarealevel1"):
        self.url_count = 0
        self.just_index = just_index
        self.register_end = register_end
        self.client = LDAPIClient(
            "http://linked.data.gov.au/dataset/asgs2016",
            url_remapper=LDAPI_CLIENT_REMAPPER
        )
        self.register = self.client.register("http://linked.data.gov.au/dataset/asgs2016/{}/".format(self.register_end))

def main():
    e = ASGSFeatureExporter(register_end="meshblock")
    e.export(limit=3000, mode="csv")
    #e.export(limit=3000, mode="excel")
    e = ASGSFeatureExporter(register_end="statisticalarealevel1")
    e.export(limit=3000, mode="csv")
    #e.export(limit=3000, mode="excel")
    e = ASGSFeatureExporter(register_end="statisticalarealevel2")
    e.export(limit=2292, mode="csv")
    #e.export(limit=2292, mode="excel")
    e = ASGSFeatureExporter(register_end="statisticalarealevel3")
    e.export(limit=340, mode="csv")
    #e.export(limit=340, mode="excel")
    e = ASGSFeatureExporter(register_end="statisticalarealevel4")
    e.export(limit=89, mode="csv")
    #e.export(limit=89, mode="excel")
    e = ASGSFeatureExporter(register_end="stateorterritory")
    e.export(mode="csv")
    #e.export(mode="excel")
    # e = ASGSFeatureExporter(just_index=False, register_end="australia")
    # e.export(mode="csv")
    # e.export(mode="excel")


def main_multisheet_workbook():
    workbook = xlsxwriter.Workbook('asgs_test2.xlsx')
    e2 = ASGSFeatureExporter(just_index=False, register_end="meshblock")
    e2.export(limit=3000, workbook=workbook, worksheet_name="Meshblock", mode="excel")
    e2 = ASGSFeatureExporter(just_index=False, register_end="statisticalarealevel1")
    e2.export(limit=3000, workbook=workbook, worksheet_name="SA1", mode="excel")
    e2 = ASGSFeatureExporter(just_index=False, register_end="statisticalarealevel2")
    e2.export(limit=2292, workbook=workbook, worksheet_name="SA2", mode="excel")
    e2 = ASGSFeatureExporter(just_index=False, register_end="statisticalarealevel3")
    e2.export(limit=340, workbook=workbook, worksheet_name="SA3", mode="excel")
    e2 = ASGSFeatureExporter(just_index=False, register_end="statisticalarealevel4")
    e2.export(limit=89, workbook=workbook, worksheet_name="SA4", mode="excel")
    e2 = ASGSFeatureExporter(just_index=False, register_end="stateorterritory")
    e2.export(workbook=workbook, worksheet_name="State", mode="excel")
    workbook.close()


if __name__ == "__main__":
    main()
    #main_multisheet_workbook()

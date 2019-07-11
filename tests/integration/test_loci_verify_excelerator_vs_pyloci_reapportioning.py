import pytest
import os
from dotenv import load_dotenv, find_dotenv
import json
from os import listdir
import csv

load_dotenv(find_dotenv())

def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]


def read_pyloci_results_csv_into_sorted_data(csvfile):
    csvdata = {}
    with open(csvfile, mode='r') as csv_file:    
        f_csv = csv.reader(csv_file) 
        #ignore header
        headers = next(f_csv) 
        for row in f_csv:
            #only keep the last 2 out of 4 cols
            curr_uri = row[2]
            curr_val = row[3]

            if curr_uri not in csvdata:
                csvdata[curr_uri] = []
            csvdata[curr_uri].append(curr_val)

        #sort by first col
        #sorted(csvdata,key=lambda x: x[1])  
    return csvdata


def read_excelerator_results_csv_into_sorted_data(csvfile):
    csvdata = {}
    with open(csvfile, mode='r') as csv_file:    
        f_csv = csv.reader(csv_file) 
        #ignore header
        headers = next(f_csv) 
        for row in f_csv:
            #get first 2 cols
            curr_uri = row[0]
            curr_val = row[1]

            if curr_uri not in csvdata:
                csvdata[curr_uri] = []
            csvdata[curr_uri].append(curr_val)     
        #sort by first col 
        #sorted(csvdata,key=lambda x: x[1])
    return csvdata

def add_failed_test_report(report_dict, test_case, failed_condition, uri, data):
    if test_case not in report_dict:
        report_dict[test_case] = []
    
    report_dict[test_case].append([failed_condition, uri, data])
    return report_dict


def test_loci_reapportioning_results_comparable():
    excelerator_results_dir = "./loci-testdata/excelerator/meteor_app_result"
    excelerator_results_prefix = "converted - "
    pyloci_results_dir = "./loci-testdata/excelerator/result"
    pyloci_results_prefix = "result_"

    excelerator_res_filenames = find_csv_filenames(excelerator_results_dir)
    pyloci_res_filenames = find_csv_filenames(pyloci_results_dir)

    # format: testcase | failed_test | uri | note
    report_dict = {}


    basename_list = []
    for fname in excelerator_res_filenames:
        print(fname)
        #store the base file name
        basename_list.append(fname.split(excelerator_results_prefix)[1])

    for b in basename_list:
        curr_excelerator_res = excelerator_results_dir + "/" + excelerator_results_prefix + b
        curr_pyloci_res = pyloci_results_dir + "/" + pyloci_results_prefix + b

        #read both csv files
        curr_excelerator_data = read_excelerator_results_csv_into_sorted_data(curr_excelerator_res)
        curr_pyloci_data = read_pyloci_results_csv_into_sorted_data(curr_pyloci_res)

        #print(json.dumps(curr_excelerator_data, indent=3))
        #print(json.dumps(curr_pyloci_data, indent=3))

        #check if key count match
        key_count_match = False
        key_values_match = False
        values_for_each_key_match = False
        if len(curr_excelerator_data.keys()) == len(curr_pyloci_data.keys()):
            print("Key count matches")
            key_count_match = True
            print( "  {}: {}".format(curr_excelerator_res, len(curr_excelerator_data.keys())))
            print( "  {}: {}".format(curr_pyloci_res, len(curr_pyloci_data.keys())))

            #check if list of keys differ
            diff = list(set(curr_excelerator_data.keys()) - set(curr_pyloci_data.keys()))
            if(len(diff) == 0):
                key_values_match = True
            else:
                key_values_match = False
                report_dict = add_failed_test_report(report_dict, b, 'key_values_not_matching', None, diff)
                

            #check if values for each key differs
            for key in curr_excelerator_data.keys():
                e_val_list = curr_excelerator_data[key]
                p_val_list = curr_pyloci_data[key]

                if(len(e_val_list) != len(p_val_list)):
                    print("Item count for {} differs".format(key))
                    print("excelerator: " + str(e_val_list))
                    print("pyloci: " + str(p_val_list))
                    report_dict = add_failed_test_report(report_dict, b, 'item_count_differs', key, "excelerator: " + str(e_val_list) + "; pyloci: " + str(p_val_list))

                else:
                    if len(e_val_list) == 1 and len(p_val_list) == 1:
                        e_val = float(e_val_list[0])
                        p_val = float(p_val_list[0])
                        diff = e_val - p_val
                        percent_of_e_val = diff/e_val*100
                        print("Diff: {}, Percent of e_val: {}".format(diff, percent_of_e_val))
                        if abs(percent_of_e_val) > 10:
                            report_dict = add_failed_test_report(report_dict, b, 'value_reapportioned_diff_exceeds_10percent', key, "Diff: {}, Percent of e_val: {}".format(diff, percent_of_e_val))
                            print("Diff is > 10%!")
                        
                    else:
                        print('Not handled yet!')

        else:
            print("Key count does not match!")
            key_count_match = False
            print( "  {}: {}".format(curr_excelerator_res, len(curr_excelerator_data.keys())))
            print( "  {}: {}".format(curr_pyloci_res, len(curr_pyloci_data.keys())))
            diff = list(set(curr_excelerator_data.keys()) - set(curr_pyloci_data.keys()))
            print(diff)
            report_dict = add_failed_test_report(report_dict, b, 'key_count_match_invalid', '', str(diff))


        print()
        



        #check if keys match
        
        #for ekey in curr_excelerator_data.keys():
        #    for pkey in curr_pyloci_data.keys():
    print(json.dumps(report_dict, indent=3))
    assert len(report_dict.keys()) == 0
     

        #for e_row in curr_excelerator_data:
        #    for p_row in curr_pyloci_data:
        #        print("e: " + str(e_row))
        #        print("p: " + str(p_row))




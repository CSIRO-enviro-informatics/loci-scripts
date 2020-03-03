from SPARQLWrapper import SPARQLWrapper, JSON
import json 
import os
import sys
import argparse
import re
import csv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from .sparql import util

GRAPHDB_USER = os.getenv("GRAPHDB_USER")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")
SPARQL_ENDPOINT =  os.getenv("SPARQL_ENDPOINT")


def run_query(curr, sparql_endpoint, auth):
    print("Querying contained areas for " + curr)
    res = util.query_mb16cc_contains(curr, sparql_endpoint, auth=auth)
    sum = 0.0
    fromArea = 0.0
    for d in res:
        sum = float(sum) + float(d['toArea'])
        fromArea = float(d['fromArea'])
    print("sum toArea: " + str(sum))
    print("fromArea: " + str(fromArea))
    print("diff: " + str(fromArea-sum) + "\n")

def read_data_from_input_csv(csvfile):
    '''Read data from csv into rows 
    '''
    csvdata = []
    print(csvfile)
    with open(csvfile, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            csvdata.append(row)
    return csvdata


def print_row(orderedDictRow):
    field1 = orderedDictRow.popitem(last=False) 
    field2 = orderedDictRow.popitem(last=False) 
        
    line = '{:>15} {:<20}\n{:>15} {:<20}\n'.format(
        field1[0], field1[1],
        field2[0], field2[1]
    )
    print(line)
    return (field1,field2)

def normalise_matches(inputmatch_list):
    data_list = []
    for match in inputmatch_list:
        data = {}
        data['from'] = match['from']
        data['to'] = match['to']
        data['fromArea'] = match['fromAreaLinkset'] if match['fromAreaLinkset'] != None else match['fromAreaDataset']
        data['toArea'] = match['toAreaLinkset'] if match['toAreaLinkset'] != None else match['toAreaDataset']
        data['toParent'] = match['toParent']
        data['pred'] = match['pred']


        data['is_intersection_area'] = False
        if data['toParent'] != None:
            data['is_intersection_area'] = True
        data_list.append(data)

        print(match['pred'])
        #if data['fromArea'] < data['toArea']:
        if match['pred'] == 'http://www.opengis.net/ont/geosparql#sfContains':
            data['proportion'] = float(data['toArea']) / float(data['fromArea'])
        elif match['pred'] == 'http://www.opengis.net/ont/geosparql#sfWithin':
            data['proportion'] = 1 #don't scale the amount as this thing is wholely in another thing
        else:
            data['proportion'] = 0 #TODO: What other predicates could there be? default to 0 for now
        
    return data_list
            

def entrypoint(user_input_csv, verbose_mode=False, output_to_file=False, outputfile=None):
    auth = None
    # set auth only if .env has credentials
    if(GRAPHDB_USER != None and GRAPHDB_PASSWORD != None):
        auth = { 
            "user" : GRAPHDB_USER,
            "password" : GRAPHDB_PASSWORD   
        }
    
    csvdata = read_data_from_input_csv(user_input_csv)
    region_data_col_name = ''
    if verbose_mode:
        print("Input data: ")

    reapportioned = []

    for row in csvdata:
        #process_row_from_input_csv(row, SPARQL_ENDPOINT, auth=auth)
        if verbose_mode:
            (col1, col2) = print_row(row)
        else:
            col1 = row.popitem(last=False) 
            col2 = row.popitem(last=False) 
        
        #get contains for col1 - assume this to be the uri row
        region_uri  = "<" + col1[1] + ">"
        region_data_col_name = col2[0]   
        region_data_col_value = col2[1]   

        #query matches
        res_list = util.query_mb16cc_contains_or_within(region_uri, SPARQL_ENDPOINT, auth, verbose=verbose_mode)
        if verbose_mode: 
            print('No. matches: {}'.format(len(res_list)))

        #for each match, work out proportion and allocate proportional value to the matching region
        normalised = normalise_matches(res_list)

        for match in normalised:
            if verbose_mode: 
                print(json.dumps(match, indent=4))
            reapportion_value = match['proportion'] * float(region_data_col_value)

            if not(match['is_intersection_area']) and match['to'] != None:
                actual_target_uri = match['to']
            elif match['is_intersection_area'] and match['toParent'] != None:
                actual_target_uri = match['toParent']
            else:
                actual_target_uri = 'unknown'
            reapportioned.append([region_uri, region_data_col_value, actual_target_uri, reapportion_value])
    
    header = "{},{},{},{}".format("from",region_data_col_name, "to", region_data_col_name+" reapportioned")
    if output_to_file:
        with open(outputfile, 'w') as f:
            f.write(header + "\n")

            for row in reapportioned:
                line = '{},{},{},{:<10f}'.format(
                    row[0], row[1], row[2], row[3]
                )
                f.write(line)
                f.write("\n")
    else:
        print(header)
        for row in reapportioned:
            line = '{},{},{},{:<10f}'.format(
                row[0], row[1], row[2], row[3]
            )
            print(line)




if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Reapportion values from csv using Loc-I')
    parser.add_argument('--verbose', dest='verbose', action='store_true',  help="Verbose mode. Include extra print outputs (default: off)")
    parser.add_argument('-o', '--outputfile', dest='outputfile', help='specify outputfile (default: print to stdout)')
    parser.add_argument('-d', '--input-directory', dest='use_input_directory',  action='store_true', help='specify to use input directory with csv files. will outputs to filename')    
    parser.add_argument('input_csv_file_or_dir', help='input csv file or directory of csvs')

    args = parser.parse_args()

    if args.input_csv_file_or_dir:
        user_input_csv_file_or_dir = args.input_csv_file_or_dir
        is_output_to_file = False
        outputfile = None
        if args.outputfile != None:
            is_output_to_file = True
            outputfile = args.outputfile
        if args.use_input_directory:
            import glob
            #iterate over files with .csv and write to result_*.csv
            working_dir = os.path.abspath(".")
            extension = 'csv'
            os.chdir(user_input_csv_file_or_dir)
            result = glob.glob('*.{}'.format(extension))
            for csvfile in result:                
                outputfile = "result_"+csvfile
                outputfile_path = outputfile
                user_input_csv_file =  csvfile
                print("Processing " + user_input_csv_file)
                print("Emitting to... " + outputfile_path)

                entrypoint(user_input_csv_file, verbose_mode=args.verbose, output_to_file=True, outputfile=outputfile_path)
        else:
            entrypoint(args.input_csv_file_or_dir, verbose_mode=args.verbose, output_to_file=is_output_to_file, outputfile=outputfile)
    else:
        user_input_csv = None
        print("Please specify an input csv. Exiting...")
        parser.print_usage
    
    #if len(args.argv) > 1:
    #    user_input_csv = sys.argv[1]
    #    entrypoint(user_input_csv)
    #else:
    #    user_input_csv = None
    #    print("Please specify an input csv. Exiting...")
        
    

    


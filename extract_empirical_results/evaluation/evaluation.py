import os
import sys
from typing import Dict, List

import requests
import re
import csv
from bs4 import BeautifulSoup
import json


basepath = os.path.dirname(__file__)
sys.path.insert(0,os.path.abspath(os.path.join(basepath,'..', '..')))
import extract_empirical_results

sys.path.insert(0,os.path.abspath(os.path.join(basepath,'..', 'types')))
from semantic_table import SemanticTable
from table import Table, Cell

from compute_metrics import compute_metrics

table_dir = os.path.abspath(os.path.join(basepath,'..','output_dir','rel_tables'))

input_dir = os.path.abspath(os.path.join(basepath,'..','input_dir'))
reference_table_annot_file = 'ref_tables_annotations.csv'


def retrieve_gold_table(gold_table_paper, gold_table_id):
    pass


def getTETML(table_file):
    with open(os.path.join(table_dir,table_file), 'r') as tetf:
        for line in f:
            if line.startswith('<'):
                xmlstring += line
            xml = BeautifulSoup(xmlstring,'lxml')
    return xml


gold_cells = [ Cell( text='Model', rowspan=1, colspan=1), 
              Cell( text='EM', rowspan=1, colspan=1), 
              Cell( text='F1', rowspan=1, colspan=1),
              Cell( text='CNN', rowspan=1, colspan=1),
              Cell( text='35', rowspan=1, colspan=1),
              Cell( text='15', rowspan=1, colspan=1),
              Cell( text='RNN', rowspan=1, colspan=1),
              Cell( text='75', rowspan=1, colspan=1),
              Cell( text='50', rowspan=1, colspan=1)
           ]

agg_cells = [ Cell( text='Model', rowspan=1, colspan=1), 
              Cell( text='EM', rowspan=1, colspan=1), 
              Cell( text='F1', rowspan=1, colspan=1), 
              Cell( text='CNN', rowspan=1, colspan=1),
              Cell( text='35', rowspan=1, colspan=1),
              Cell( text='15', rowspan=1, colspan=1),
              Cell( text='RNN', rowspan=1, colspan=1),
              Cell( text='75', rowspan=1, colspan=1),
              Cell( text='50', rowspan=1, colspan=1)
            ]

gold_table = Table(gold_cells,3,3,'example_gold_paper_id',1,'example_caption')

aggregate_table = Table(agg_cells,3,3,'example_agg_paper_id',1,'example_caption')

print(str(gold_table)+'\n')
print(str(aggregate_table)+'\n')

metrics = compute_metrics(gold_table, aggregate_table)

#with open(os.path.join(input_dir,reference_table_annot_file), 'r') as f:
#    csv_reader = csv.DictReader(f,quotechar='"')

#    for line in csv_reader:
        # print(line['Dataset name'])
        # print(line['Dataset Paper ID'])
        # print(line['Gold Reference Paper'])
        # print(line['Gold Reference Table'])
        
#        dataset_paper_id = line['Dataset Paper ID']
#        gold_table_paper = line['Gold Reference Paper']
#        gold_table_id = line['Gold Reference Table']

        #table_file = retrieve_gold_table(dataset_paper_id, gold_table_paper, gold_table_id)
        #table_tetml = getTETML(table_file)
        # Make semantic table of gold table
        # Make semantic table of system output table

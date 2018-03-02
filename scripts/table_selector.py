import os
import subprocess
import sys
from typing import List

from bs4 import BeautifulSoup
import json
import requests
import re

basepath = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(basepath, '..', '..')))
import extract_empirical_results

sys.path.insert(0, os.path.abspath(os.path.join(basepath, '..', 'common')))
from corvid.types.table import Table
from caption import Caption

tet_path = os.path.abspath(
    os.path.join(basepath, '..', '..', 'lib', 'tet', 'bin', 'tet'))

# dataset_name = 'learning faces in the wild'
dataset_name_aliases = ['lfw', 'learning faces in the wild']

output_dir = os.path.abspath(os.path.join(basepath, '..', 'output_dir'))
tetml_dir = os.path.abspath(
    os.path.join(basepath, '..', 'output_dir', 'tetml'))


def isTableRelevant(tables_with_caption):
    """
        identify if a table from a pdf is relevant
        i.e., reports empirical results on the given dataset
    """
    tables_classified = {}
    for table_id, caption_text in tables_with_caption.items():
        for dataset_name in dataset_name_aliases:
            if dataset_name.lower() in caption_text.lower():
                tables_classified[table_id] = caption_text
                break
            else:
                tables_classified[table_id] = 0
    return tables_classified


#caption extraction using tetml
dataset_paper_hash = '370b5757a5379b15e30d619e4d3fb9e8e13f3256'
tetml_dir = os.path.abspath(
    os.path.join(basepath, '..', 'output_dir', 'tetml', dataset_paper_hash))
tables_dir = os.path.abspath(
    os.path.join(basepath, '..', 'output_dir', 'tables', dataset_paper_hash))
errors_dir = os.path.abspath(
    os.path.join(basepath, '..', 'output_dir', 'errors_dir',
                 dataset_paper_hash))
relevant_tables_dir = os.path.abspath(
    os.path.join(basepath, '..', 'output_dir', 'rel_tables',
                 dataset_paper_hash))
samples_dir = os.path.abspath(
    os.path.join(basepath, '..', 'output_dir', 'random_sample',
                 dataset_paper_hash))

captions_found = 0
num_captions = 0
num_tables = 0
num_non_caption_texts = 0
num_relevant = 0

table_sample = []
sample_counter = 0

for TETML_FILENAME in os.listdir(tetml_dir):

    tables_with_caption = {}

    if TETML_FILENAME.startswith("."):
        continue

    with open(os.path.join(tetml_dir, TETML_FILENAME), 'r') as tetf:
        print('Reading TET file', tetml_dir, '/', TETML_FILENAME)
        xml = BeautifulSoup(tetf, 'lxml')
        caption = Caption()
        tables, caption_texts, non_caption_texts = caption.find_caption(xml, 5)

    paper_id = TETML_FILENAME.split('.')[0]
    error_log_name = paper_id + '.error'

    TABLES_FILENAME = paper_id + '.tables'

    if not os.path.exists(tables_dir):
        os.makedirs(tables_dir)

    if not os.path.exists(errors_dir):
        os.makedirs(errors_dir)

    error_log = open(os.path.join(errors_dir, error_log_name), 'w')

    with open(os.path.join(tables_dir, TABLES_FILENAME), 'w') as table_file:
        for i, table in enumerate(tables):
            sample_counter += 1
            if caption_texts[i] != 'nil':
                captions_found += 1
                table_file.write(str(caption_texts[i]) + '\n')
                table_file.write(str(tables[i]) + '\n')
                table_file.write(str('-----------------------\n'))
                tables_with_caption[i] = caption_texts[i]

            else:
                error_log.write(str(tables[i]) + '\n')
                try:
                    for j, text in enumerate(non_caption_texts[i]):
                        error_log.write('Table id: ' + str(
                            i) + ' | non matched caption candidate: ' + str(
                            j) + '\n' + str(text) + '\n')
                    error_log.write('------------------------------\n')
                except Exception as e:
                    print('exception', str(e), 'index: ', i)

    num_tables += len(tables)
    num_captions += len(caption_texts)
    num_non_caption_texts += len(non_caption_texts)

    tables_classified = isTableRelevant(tables_with_caption)

    if not os.path.exists(relevant_tables_dir):
        os.makedirs(relevant_tables_dir)

    for idx, relevance in tables_classified.items():
        print('table:', idx, 'is', relevance)
        if relevance != 0:
            num_relevant += 1
            caption = tables_classified[idx]
            TABLES_FILENAME = paper_id + '_' + str(idx) + '.tables'
            with open(os.path.join(relevant_tables_dir, TABLES_FILENAME),
                      'w') as reltablefile:
                reltablefile.write(str(caption) + '\n')
                reltablefile.write(str(tables[idx]) + '\n')
                reltablefile.write(str('-----------------------\n'))

print('# of tables ', num_tables)
print('# of captions ', num_captions)
print('# of captions found ', captions_found)
print('# of non-captions found ', num_non_caption_texts)
print('# of relevant tables ', num_relevant)

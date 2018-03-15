"""

Script that takes TSV format of Madeleine's annotations and extracts
corresponding Gold Tables.

MAKES ASSUMPTION THAT EVERY DATASET HAS AT LEAST A paper_id ASSOCIATED W/ IT

"""

import csv
import json
import numpy as np
import re

def normalize(s: str) -> str:
    return re.sub('[^A-Za-z0-9\s]+', '', s).lower()


with open('misc/gold_raw_annotations.tsv', 'r') as f:
    tsv = csv.reader(f, delimiter='\t')
    tsv = np.array([row for row in tsv])

# header row
header_row = [normalize(header) for header in tsv[0, :]]
index_column_dataset_name = np.where([
    'dataset' in header and
    'name' in header and
    'alias' not in header
    for header in header_row
])[0]
index_column_dataset_aliases = np.where([
    'dataset' in header and
    'name' in header and
    'alias' in header
    for header in header_row
])[0]
index_column_dataset_paper_id = np.where([
    'dataset' in header and
    'paper' in header and
    'id' in header
    for header in header_row
])[0]
index_column_gold_paper_id = np.where([
    'gold' in header and
    'paper' in header and
    'id' in header
    for header in header_row
])[0]
index_column_gold_caption_id = np.where([
    'gold' in header and
    'table' in header and
    'caption' in header and
    'id' in header
    for header in header_row
])[0]

assert len(index_column_dataset_name) == 1
assert len(index_column_dataset_aliases) == 1
assert len(index_column_dataset_paper_id) == 1
assert len(index_column_gold_paper_id) == 1
assert len(index_column_gold_caption_id) == 1

index_column_dataset_name = index_column_dataset_name[0]
index_column_dataset_aliases = index_column_dataset_aliases[0]
index_column_dataset_paper_id = index_column_dataset_paper_id[0]
index_column_gold_paper_id = index_column_gold_paper_id[0]
index_column_gold_caption_id = index_column_gold_caption_id[0]

# find duplicate paper_ids
all_paper_ids = [paper_id for paper_id in tsv[1:, index_column_dataset_paper_id] if paper_id != '']
index_duplicates = np.where([all_paper_ids.count(paper_id) > 1 for paper_id in all_paper_ids])[0]
print(np.array(all_paper_ids)[index_duplicates])
assert len(index_duplicates) == 0


# construct JSONs from rows of TSV by filling in any missing fields
current_dataset_name = None
current_dataset_aliases = None
current_dataset_paper_id = None

datasets = {}
for i, row in enumerate(tsv):

    if i == 0:
        continue

    if row[index_column_dataset_name] != '':
        current_dataset_name = normalize(row[index_column_dataset_name])
        current_dataset_aliases = ','.join([normalize(alias)
                                            for alias in row[
                                                index_column_dataset_aliases].split(
                ',')])
        current_dataset_paper_id = normalize(row[index_column_dataset_paper_id])

    tsv[i, index_column_dataset_name] = current_dataset_name
    tsv[i, index_column_dataset_aliases] = current_dataset_aliases
    tsv[i, index_column_dataset_paper_id] = current_dataset_paper_id
    tsv[i, index_column_gold_paper_id] = normalize(tsv[i, index_column_gold_paper_id])
    tsv[i, index_column_gold_caption_id] = normalize(tsv[i, index_column_gold_caption_id])

    datasets[current_dataset_paper_id] = {
        'name': current_dataset_name,
        'aliases': None if current_dataset_aliases == '' \
            else current_dataset_aliases.split(','),
        'paper_id': current_dataset_paper_id,
        'gold_tables': []
    }

# add gold table data to each dataset json
for row in tsv[1:, :]:

    if row[index_column_gold_paper_id] == '':
        continue

    if row[index_column_gold_caption_id] == '':
        continue

    # find corresponding dataset
    dataset = datasets.get(normalize(row[index_column_dataset_paper_id]))
    if dataset:
        paper_id = normalize(row[index_column_gold_paper_id])
        caption_id = normalize(row[index_column_gold_caption_id])
        dataset['gold_tables'].append(
            {
                'paper_id': paper_id,
                'caption_id': caption_id
            })

datasets = [dataset for dataset in datasets.values()]

with open('data/datasets.json', 'w') as f:
    json.dump(datasets, f)

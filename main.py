"""

Executes entire table aggregation pipeline

    Input: `datasets.json` containing `paper_id` for each dataset of interest
    Output: `agg_tables.json` containing aggregated tables per dataset

INPUT FORMAT:
[
    {
      "name": "dataset name",
      "aliases": [
         "alias 1",
         "alias 2"
      ],
      "paper_id": "dataset paper id",
      "gold_tables": [
         {
            "paper_id": "gold paper id",
            "caption_id": "table * (taken from beginning of caption)"
         }
      ]
   },
   {
      "name": "other dataset name",
      "aliases": null,
      "paper_id": null,
      "gold_tables": null
   },
   ...
]


PSEUDOCODE:
for dataset in datasets:
    load_metadata_about_dataset()

    tables = []
    papers = find_relevant_papers(dataset)
    for paper in papers:
        pdf_path = fetch_pdf(paper)
        xml_path = parse_pdf(pdf_path)
        tables.add(extract_tables(xml_path))

    normalize(tables)
    filter_relevant(tables)

    gold_tables = load_gold_tables(dataset)
    for gold_table in gold_tables:
        target_schema = gold_table.schema
        dont_cheat = [table for table in tables if table.paper_id != gold_table.paper_id]
        pred_table = aggregate_tables(dont_cheat, target_schema)
        metrics = evaluate_metrics(gold_table, pred_table)
        save(dataset, pred_table, metrics)
"""

import os
import json
import re

try:
    import cPickle as pickle
except:
    import pickle

from typing import List, Dict, Tuple

from bs4 import BeautifulSoup

from src.s2base.s2base.elastic import citations_lookup, default_es_client

from corvid.types.table import Table, EMPTY_CAPTION
from corvid.types.dataset import Dataset

from corvid.table_extraction.table_extractor import TetmlTableExtractor

from corvid.schema_matcher.schema_matcher import ColNameSchemaMatcher

from corvid.evaluation.compute_metrics import compute_metrics

from corvid.util.files import is_url_working, read_one_json_from_es, \
    fetch_one_pdf_from_s3
from corvid.util.tetml import parse_one_pdf

from corvid.util.strings import remove_non_alphanumeric

from config import DATASETS_JSON, ES_PROD_URL, S3_PDFS_URL, PDF_DIR, \
    TET_BIN_PATH, TETML_DIR, PICKLE_DIR, JSON_DIR, AGGREGATION_PICKLE_DIR,\
    convert_paper_id_to_s3_filename, convert_paper_id_to_es_endpoint

CAPTION_SEARCH_WINDOW = 3




def find_tables_from_paper_ids(paper_ids: List[str]) -> Tuple[Dict[str, Table], Dict]:
    """For each `paper_id`, iteratively performs:

        * fetch PDF
        * parse PDF to TETML
        * extract tables from TETML

    Loop continues even if any of these components fails, but updates
    the `log_summary` with error statistics

    Returns extracted tables in format:
        {
            'paper_id': [table1, table2],
            'paper_id': [table3],
            'paper_id': [table4], [table5], [table6]
        }
    """

    log_summary = {
        'num_paper_ids': len(paper_ids),
        'fetch_pdf_from_s3': {
            'success': 0,
            'fail': 0,
            'skip': 0
        },
        'parse_pdf_to_tetml': {
            'success': 0,
            'fail': 0,
            'skip': 0
        },
        'extract_tables_from_tetml': {
            'success': 0,
            'fail': 0,
            'skip': 0
        }
    }

    all_tables = {}
    for paper_id in paper_ids:

        # fetch PDFs of relevant papers
        pdf_path = '{}.pdf'.format(os.path.join(PDF_DIR, paper_id))
        if not os.path.exists(pdf_path):
            try:
                output_path = fetch_one_pdf_from_s3(
                    s3_url=S3_PDFS_URL,
                    paper_id=paper_id,
                    out_dir=PDF_DIR,
                    convert_paper_id_to_s3_filename=convert_paper_id_to_s3_filename,
                    is_overwrite=True)
                assert output_path == pdf_path
                log_summary['fetch_pdf_from_s3']['success'] += 1
            except Exception as e:
                print(e)
                log_summary['fetch_pdf_from_s3']['fail'] += 1
                continue
        else:
            log_summary['fetch_pdf_from_s3']['skip'] += 1

        # parse each PDF to TETML
        tetml_path = '{}.tetml'.format(os.path.join(TETML_DIR, paper_id))
        if not os.path.exists(tetml_path):
            try:
                output_path = parse_one_pdf(tet_path=TET_BIN_PATH,
                                           pdf_path=pdf_path,
                                           out_dir=TETML_DIR,
                                           is_overwrite=True)
                assert output_path == tetml_path
                log_summary['parse_pdf_to_tetml']['success'] += 1
            except Exception as e:
                print(e)
                log_summary['parse_pdf_to_tetml']['fail'] += 1
                continue
        else:
            log_summary['parse_pdf_to_tetml']['skip'] += 1

        # extract tables from TETML or load if already exists
        pickle_path = '{}.pickle'.format(os.path.join(PICKLE_DIR, paper_id))
        if not os.path.exists(pickle_path):
            try:
                with open(tetml_path, 'r') as f_tetml:
                    tables = TetmlTableExtractor.extract_tables(
                        tetml=BeautifulSoup(f_tetml),
                        paper_id=paper_id,
                        caption_search_window=CAPTION_SEARCH_WINDOW)
                with open(pickle_path, 'wb') as f_pickle:
                    pickle.dump(tables, f_pickle)
                log_summary['extract_tables_from_tetml']['success'] += 1
            except Exception as e:
                print(e)
                log_summary['extract_tables_from_tetml']['fail'] += 1
                continue
        else:
            with open(pickle_path, 'rb') as f_pickle:
                tables = pickle.load(f_pickle)
            log_summary['extract_tables_from_tetml']['skip'] += 1

        all_tables[paper_id] = tables

    return all_tables, log_summary




def create_dataset(name: str,
                   aliases: List[str],
                   paper_id: str,
                   gold_table_ids: List[Dict]) -> Tuple[Dataset, Dict]:
    """Creates a Dataset object given a single JSON from `datasets.json`.

    Returns `None` if invalid JSON.

    A `gold_table_id` is a Dict containing fields used to identify the table
    within the specific paper.  For example, a `gold_paper_id` and
    `caption_id` pair can be used to identify a specific table.

    """

    log_summary = {
        'find_tables_from_gold_paper_ids': dict(),
        'num_candidate_gold_tables': 0,
        'num_relevant_gold_tables': 0
    }

    unique_gold_paper_ids = list(set([id.get('paper_id') for id in gold_table_ids]))
    candidate_gold_tables, sub_log = find_tables_from_paper_ids(paper_ids=unique_gold_paper_ids)
    log_summary['find_tables_from_gold_paper_ids'] = sub_log

    if len(candidate_gold_tables) < 1:
        return None, log_summary

    # TODO: consider omnipage parsing of deepfigures images instead of noisy matching
    #
    # identify relevant gold tables among candidates by matching their captions to caption_id
    #
    # e.g. does the caption begin with 'table iv' from paper '12345'?
    #
    relevant_gold_tables = []
    for gold_table_id in gold_table_ids:

        relevant_gold_paper_id =  gold_table_id.get('paper_id')
        relevant_gold_caption_id = remove_non_alphanumeric(gold_table_id.get('caption_id')).lower()

        # not all gold paper ids are represented among candidates (i.e. failed extraction); skip these
        if not candidate_gold_tables.get(relevant_gold_paper_id):
            continue

        # otherwise, match candidate gold tables based on relevant caption id
        for candidate_gold_table in candidate_gold_tables.get(relevant_gold_paper_id):
            log_summary['num_candidate_gold_tables'] += 1

            # TODO: matching is noisy, so doesnt lead to a single table per gold_table_id
            is_contains_caption_id = remove_non_alphanumeric(candidate_gold_table.caption).lower().startswith(relevant_gold_caption_id)

            if candidate_gold_table.caption != EMPTY_CAPTION and is_contains_caption_id:
                relevant_gold_tables.append(candidate_gold_table)
                log_summary['num_relevant_gold_tables'] += 1

    # TODO: `cited_by_paper_ids` unused for now
    return Dataset(name=name,
                   paper_id=paper_id,
                   aliases=aliases,
                   gold_tables=relevant_gold_tables,
                   cited_by_paper_ids=[]), log_summary




if __name__ == '__main__':
    with open(DATASETS_JSON, 'r') as f_datasets:
        dataset_jsons = json.load(f_datasets)

    # verify external dependencies
    assert is_url_working(ES_PROD_URL)
    es_client = default_es_client(ES_PROD_URL)
    #assert is_url_working(S3_PDFS_URL)
    assert os.path.exists(TET_BIN_PATH)


    schema_matcher = ColNameSchemaMatcher()

    log_summary = {
        'num_dataset_without_paper_id': 0,
        'num_dataset_without_gold_tables': 0
    }

    for dataset_json in dataset_jsons:

        dataset_paper_id = dataset_json.get('paper_id')
        if not dataset_paper_id:
            log_summary['num_dataset_without_paper_id'] += 1
            continue

        gold_table_ids = dataset_json.get('gold_tables')
        if not gold_table_ids or len(gold_table_ids) < 1:
            log_summary['num_dataset_without_gold_tables'] += 1
            continue

        log_summary[dataset_paper_id] = {
            'create_dataset': dict()
        }

        dataset, sub_log_dataset = create_dataset(
            name=remove_non_alphanumeric(dataset_json.get('name')),
            aliases=[remove_non_alphanumeric(alias) for alias in set(dataset_json.get('aliases'))] if dataset_json.get('aliases') else [],
            paper_id=dataset_paper_id,
            gold_table_ids=gold_table_ids
        )
        log_summary[dataset_paper_id]['create_dataset'] = sub_log_dataset

        if dataset is None:
            continue

        outputs = []
        for gold_table in dataset.gold_tables:

            # TODO: temp restrict to only papers cited by gold paper
            relevant_source_paper_ids = citations_lookup(paper_id=gold_table.paper_id,
                                                         es_client=es_client)
            relevant_source_tables, _ = find_tables_from_paper_ids(paper_ids=relevant_source_paper_ids)

            pairwise_mappings = schema_matcher.map_tables(
                tables=[table for tables in relevant_source_tables.values() for table in tables],
                target_schema=gold_table
            )
            aggregate_table = schema_matcher.aggregate_tables(
                pairwise_mappings=pairwise_mappings,
                target_schema=gold_table
            )

            outputs.append({
                'gold': gold_table,
                'pred': aggregate_table,
                'score': compute_metrics(gold_table=gold_table,
                                         pred_table=aggregate_table)
            })

        agg_pickle_path = '{}.pickle'.format(
            os.path.join(AGGREGATION_PICKLE_DIR, dataset_paper_id))
        with open(agg_pickle_path, 'wb') as f_output:
            pickle.dump(outputs, f_output)




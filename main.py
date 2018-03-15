"""

Executes entire table aggregation pipeline

    Input: `datasets.json` containing `paper_id` for each dataset of interest
    Output: `agg_tables.json` containing aggregated tables per dataset


for dataset in datasets:
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

from corvid.types.table import Table, EMPTY_CAPTION

from corvid.table_extraction.table_extractor import TetmlTableExtractor

from corvid.util.files import is_url_working, read_one_json_from_es, \
    fetch_one_pdf_from_s3
from corvid.util.tetml import parse_one_pdf

from corvid.util.strings import remove_non_alphanumeric

from config import DATASETS_JSON, ES_PROD_URL, S3_PDFS_URL, PDF_DIR, \
    TET_BIN_PATH, TETML_DIR, PICKLE_DIR, convert_paper_id_to_s3_filename, \
    convert_paper_id_to_es_endpoint

CAPTION_SEARCH_WINDOW = 3

# TODO: load from local if exists, else ...
def find_tables_from_paper_ids(paper_ids: List[str]) -> Tuple[Dict[str, Table], Dict]:
    """For each `paper_id`, iteratively performs:

        * fetch PDF
        * parse PDF to TETML
        * extract tables from TETML

    Loop continues even if any of these components fails, but updates
    the `log_summary` with error statistics
    """

    log_summary = {
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


if __name__ == '__main__':
    with open(DATASETS_JSON, 'r') as f_datasets:
        datasets = json.load(f_datasets)

    # verify external dependencies
    assert is_url_working(ES_PROD_URL)
    #assert is_url_working(S3_PDFS_URL)
    assert os.path.exists(TET_BIN_PATH)

    log_summary = {}

    for dataset in datasets:

        dataset_name = remove_non_alphanumeric(dataset.get('name'))
        dataset_aliases = [
            remove_non_alphanumeric(alias) for alias in dataset.get('aliases')
        ] if dataset.get('aliases') else []
        dataset_paper_id = dataset.get('paper_id')

        # logging
        log_summary[dataset_paper_id] = {
            'dataset_paper_id': None,
            'find_gold_tables': None,
            'num_candidate_gold_tables': 0,
            'num_identified_gold_tables': 0,
            'fetch_dataset_paper_json_from_es': None,
            'find_source_tables': None,
            'num_all_source_tables': 0,
            'num_relevant_source_tables': 0,
        }

        if not dataset_paper_id:
            log_summary[dataset_paper_id]['dataset_paper_id'] = 'MISSING'
            continue

        #
        # collect candidate gold tables for this dataset
        #
        if not dataset.get('gold_tables'):
            log_summary[dataset_paper_id]['find_gold_tables'] = 'MISSING'
            continue

        gold_paper_ids = [
            gold_table_dict.get('paper_id')
            for gold_table_dict in dataset.get('gold_tables')
        ]
        candidate_gold_tables, log_summary[dataset_paper_id]['find_gold_tables'] = \
            find_tables_from_paper_ids(paper_ids=gold_paper_ids)
        if len(candidate_gold_tables) < 1:
            continue

        #
        # identify gold tables based on matching caption id
        #
        gold_caption_ids = [
            remove_non_alphanumeric(gold_table_dict.get('caption_id')).lower()
            for gold_table_dict in dataset.get('gold_tables')
        ]
        identified_gold_tables = []
        for tables in candidate_gold_tables.values():
            log_summary[dataset_paper_id]['num_candidate_gold_tables'] += len(tables)
            for table in tables:
                is_has_caption = table.caption != EMPTY_CAPTION
                is_contains_caption_id = any([
                    remove_non_alphanumeric(table.caption).lower().startswith(caption_id)
                    for caption_id in gold_caption_ids
                ])
                if is_has_caption and is_contains_caption_id:
                    identified_gold_tables.append(table)

        log_summary[dataset_paper_id]['num_identified_gold_tables'] = len(identified_gold_tables)

        #
        # fetch dataset paper JSON & find paper_ids that cite this dataset
        #
        try:
            dataset_paper_json = read_one_json_from_es(
                es_url=ES_PROD_URL,
                paper_id=dataset_paper_id,
                convert_paper_id_to_es_endpoint=convert_paper_id_to_es_endpoint)
            relevant_paper_ids = dataset_paper_json.get('citedBy')
        except Exception as e:
            print(e)
            log_summary[dataset_paper_id]['fetch_dataset_paper_json_from_es'] = 'FAIL'
            continue

        #
        # collect all Tables from relevant paper_ids
        #
        all_source_tables, log_summary[dataset_paper_id]['find_source_tables'] = \
            find_tables_from_paper_ids(paper_ids=relevant_paper_ids)
        if len(all_source_tables) < 1:
            continue

        #
        # filter Tables based on (1) has caption, (2) caption contains dataset name and/or alias
        #
        # TODO: soft matching for multiword aliases
        relevant_source_tables = []
        for tables in all_source_tables.values():
            log_summary[dataset_paper_id]['num_all_source_tables'] += len(tables)
            for table in tables:
                is_has_caption = table.caption != EMPTY_CAPTION
                is_contains_name_or_alias = any([
                    name in remove_non_alphanumeric(table.caption).lower()
                    for name in [dataset_name] + dataset_aliases
                ])
                if is_has_caption and is_contains_name_or_alias:
                    relevant_source_tables.append(table)

        log_summary[dataset_paper_id]['num_relevant_source_tables'] = len(relevant_source_tables)


    # log summaries
    print('Datasets with/without gold tables: {}/{}'.format(
        sum([d.get('find_gold_tables') != 'MISSING' for d in
             log_summary.values()]),
        sum([d.get('find_gold_tables') == 'MISSING' for d in
             log_summary.values()])
    ))

    print('Gold PDFs success/fail/skip fetch from S3: {}/{}/{}'.format(
        sum([dd.get('fetch_pdf_from_s3').get('success') for dd in
             [d.get('find_gold_tables') for d in log_summary.values()] if
             dd != 'MISSING']),
        sum([dd.get('fetch_pdf_from_s3').get('fail') for dd in
             [d.get('find_gold_tables') for d in log_summary.values()] if
             dd != 'MISSING']),
        sum([dd.get('fetch_pdf_from_s3').get('skip') for dd in
             [d.get('find_gold_tables') for d in log_summary.values()] if
             dd != 'MISSING'])
    ))

    print('Gold PDFs success/fail/skip parse to TETML: {}/{}/{}'.format(
        sum([dd.get('parse_pdf_to_tetml').get('success') for dd in
             [d.get('find_gold_tables') for d in log_summary.values()] if
             dd != 'MISSING']),
        sum([dd.get('parse_pdf_to_tetml').get('fail') for dd in
             [d.get('find_gold_tables') for d in log_summary.values()] if
             dd != 'MISSING']),
        sum([dd.get('parse_pdf_to_tetml').get('skip') for dd in
             [d.get('find_gold_tables') for d in log_summary.values()] if
             dd != 'MISSING'])
    ))

    print('Gold TETML success/fail/skip Table Extractor: {}/{}/{}'.format(
        sum([dd.get('extract_tables_from_tetml').get('success') for dd in
             [d.get('find_gold_tables') for d in log_summary.values()] if
             dd != 'MISSING']),
        sum([dd.get('extract_tables_from_tetml').get('fail') for dd in
             [d.get('find_gold_tables') for d in log_summary.values()] if
             dd != 'MISSING']),
        sum([dd.get('extract_tables_from_tetml').get('skip') for dd in
             [d.get('find_gold_tables') for d in log_summary.values()] if
             dd != 'MISSING'])
    ))

    print('Gold candidate/usable tables: {}/{}'.format(
        sum([d.get('num_candidate_gold_tables') for d in log_summary.values()]),
        sum([d.get('num_identified_gold_tables') for d in log_summary.values()])
    ))

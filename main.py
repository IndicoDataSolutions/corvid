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

from corvid.schema_matcher.schema_matcher import ColNameSchemaMatcher

from corvid.evaluation.compute_metrics import compute_metrics

from corvid.util.files import is_url_working, read_one_json_from_es, \
    fetch_one_pdf_from_s3
from corvid.util.tetml import parse_one_pdf

from corvid.util.strings import remove_non_alphanumeric

from config import DATASETS_JSON, ES_PROD_URL, S3_PDFS_URL, PDF_DIR, \
    TET_BIN_PATH, TETML_DIR, PICKLE_DIR, JSON_DIR, AGGREGATION_PICKLE_PATH,\
    convert_paper_id_to_s3_filename, convert_paper_id_to_es_endpoint

CAPTION_SEARCH_WINDOW = 3


# TODO: load from local if exists, else ...
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

    outputs = {dataset.get('paper_id'): [] for dataset in datasets}
    for dataset in datasets:

        #
        # get metadata about dataset
        #
        dataset_name = remove_non_alphanumeric(dataset.get('name'))
        dataset_aliases = [
            remove_non_alphanumeric(alias) for alias in dataset.get('aliases')
        ] if dataset.get('aliases') else []
        dataset_paper_id = dataset.get('paper_id')

        if dataset_paper_id != '0f8468de03ee9f12d693237bec87916311bf1c24':
            continue

        # initialize logging
        log_summary[dataset_paper_id] = {
            'fetch_dataset_paper': {
                'paper_id': None,
                'from_es': None
            },
            'process_gold_papers': None,
            'extract_gold_tables': {
                'num_candidate': 0,
                'num_relevant': 0,
            },
            'relevant_source_papers': None,
            'process_source_papers': None,
            'extract_source_tables': {
                'num_candidate': 0,
                'num_relevant': 0
            }
        }

        #
        # verify dataset has a paper associated with it
        #
        if not dataset_paper_id:
            log_summary[dataset_paper_id]['fetch_dataset_paper']['paper_id'] = 'MISSING'
            continue
        log_summary[dataset_paper_id]['fetch_dataset_paper']['paper_id'] = 'EXISTS'

        #
        # fetch dataset paper JSON (used later to find relevant source papers)
        #
        json_path = '{}.json'.format(os.path.join(JSON_DIR, dataset_paper_id))
        if not os.path.exists(json_path):
            try:
                dataset_paper_json = read_one_json_from_es(
                    es_url=ES_PROD_URL,
                    paper_id=dataset_paper_id,
                    convert_paper_id_to_es_endpoint=convert_paper_id_to_es_endpoint)
                with open(json_path, 'w') as f_json:
                    json.dump(dataset_paper_json, f_json)
                log_summary[dataset_paper_id]['fetch_dataset_paper']['from_es'] = 'SUCCESS'
            except Exception as e:
                print(e)
                log_summary[dataset_paper_id]['fetch_dataset_paper']['from_es'] = 'FAIL'
                continue
        else:
            with open(json_path, 'r') as f_json:
                dataset_paper_json = json.load(f_json)
            log_summary[dataset_paper_id]['fetch_dataset_paper']['from_es'] = 'SKIP'

        #
        # [FOR GOLD EVAL 1] get metadata about dataset's gold tables
        #
        dataset_gold_tables = dataset.get('gold_tables')
        if not dataset_gold_tables:
            log_summary[dataset_paper_id]['process_gold_papers'] = 'MISSING'
            continue
        log_summary[dataset_paper_id]['process_gold_papers'] = 'EXISTS'

        #
        # [FOR GOLD EVAL 2] extract candidate gold tables for this dataset
        #
        #    for each dataset, `candidate_gold_tables` looks like
        #    {
        #        'paper_id': [table1, table2],
        #        'paper_id': [table3],
        #        'paper_id': [table4], [table5], [table6]
        #    }
        candidate_gold_tables, sub_log = \
            find_tables_from_paper_ids(paper_ids=[
                d.get('paper_id') for d in dataset_gold_tables
            ])
        log_summary[dataset_paper_id]['process_gold_papers'] = sub_log
        if len(candidate_gold_tables) < 1:
            continue

        #
        # [FOR GOLD EVAL 3] identify gold tables using their captions
        #  e.g. does `table.caption` start with 'table iv', where 'table iv'
        #       is one of the `caption_id`?
        #
        #  these "relevant" gold tables are the ones used for evaluation
        #
        relevant_gold_tables = []
        for tables in candidate_gold_tables.values():
            log_summary[dataset_paper_id]['extract_gold_tables']['num_candidate'] += len(tables)
            for table in tables:
                is_has_caption = table.caption != EMPTY_CAPTION
                is_contains_caption_id = any([
                    remove_non_alphanumeric(table.caption).lower().startswith(
                        remove_non_alphanumeric(d.get('caption_id')).lower())
                    for d in dataset_gold_tables
                ])
                if is_has_caption and is_contains_caption_id:
                    relevant_gold_tables.append(table)

        log_summary[dataset_paper_id]['extract_gold_tables']['num_relevant'] = len(relevant_gold_tables)

        #
        # [FOR SOURCE TABLES 1] collect paper_ids that might contain
        # relevant tables for aggregation.  currently, this is based on
        #   * did this paper cite the dataset?
        #
        relevant_paper_ids = dataset_paper_json.get('citedBy')
        log_summary[dataset_paper_id]['relevant_source_papers'] = len(relevant_paper_ids)
        if len(candidate_gold_tables) < 1:
            continue

        #
        # [FOR SOURCE TABLES 2] extract all Tables from relevant source papers
        #
        #    for each source paper, `source_table` looks like
        #    {
        #        'paper_id': [table1, table2],
        #        'paper_id': [table3],
        #        'paper_id': [table4], [table5], [table6]
        #    }
        all_source_tables, sub_log = \
            find_tables_from_paper_ids(paper_ids=relevant_paper_ids)
        log_summary[dataset_paper_id]['process_source_papers'] = sub_log
        if len(all_source_tables) < 1:
            continue

        #
        # [FOR SOURCE TABLES 3] identify source tables using their captions
        #  e.g. does `table.caption` contain 'mnist', where 'mnist'
        #       is the dataset name or one of its aliases?
        #
        #  these "relevant" source tables are the ones used for aggregation
        #
        # TODO: soft matching for multiword aliases
        relevant_source_tables = []
        for tables in all_source_tables.values():
            log_summary[dataset_paper_id]['extract_source_tables']['num_candidate'] += len(tables)
            for table in tables:
                is_has_caption = table.caption != EMPTY_CAPTION
                is_contains_name_or_alias = any([
                    name in remove_non_alphanumeric(table.caption).lower()
                    for name in [dataset_name] + dataset_aliases
                ])
                if is_has_caption and is_contains_name_or_alias:
                    relevant_source_tables.append(table)

        log_summary[dataset_paper_id]['extract_source_tables']['num_relevant'] = len(relevant_source_tables)


        #
        # [AGGREGATE TABLES] in our experiments, the `target_schema` is
        # an empty (header-only) version of a gold table
        #
        schema_matcher = ColNameSchemaMatcher()
        for gold_table in relevant_gold_tables:

            # TODO: make sure this would still work even with `target_schema = gold_table`
            gold_header_row = gold_table[0, :]
            target_schema = Table.create_from_grid(grid=[gold_header_row])

            #
            # [AGGREGATE TABLES 1] remove gold tables from source tables list
            #


            #
            # [AGGREGATE TABLES 2] aggregate source tables to a single table
            #
            pairwise_mappings = schema_matcher.map_tables(
                tables=relevant_source_tables,
                target_schema=target_schema
            )
            aggregate_table = schema_matcher.aggregate_tables(
                pairwise_mappings=pairwise_mappings,
                target_schema=target_schema
            )

            #
            # [AGGREGATE TABLES 3] evaluation
            #
            outputs[dataset_paper_id].append({
                'gold': gold_table,
                'pred': aggregate_table,
                'score': compute_metrics(gold_table=gold_table,
                                         pred_table=aggregate_table)
            })

    #
    # save results
    #
    with open(AGGREGATION_PICKLE_PATH, 'wb') as f_output:
        pickle.dump(outputs, f_output)

    #
    # log summaries
    #
    print('Datasets with/without gold tables: {}/{}'.format(
        sum([d.get('process_gold_papers') != 'MISSING' for d in
             log_summary.values() if d.get('process_gold_papers')]),
        sum([d.get('process_gold_papers') == 'MISSING' for d in
             log_summary.values() if d.get('process_gold_papers')])
    ))

    print('Gold PDFs success/fail/skip fetch from S3: {}/{}/{}'.format(
        sum([dd.get('fetch_pdf_from_s3').get('success') for dd in
             [d.get('process_gold_papers') for d in log_summary.values()
              if d.get('process_gold_papers')] if dd != 'MISSING']),
        sum([dd.get('fetch_pdf_from_s3').get('fail') for dd in
             [d.get('process_gold_papers') for d in log_summary.values()
              if d.get('process_gold_papers')] if dd != 'MISSING']),
        sum([dd.get('fetch_pdf_from_s3').get('skip') for dd in
             [d.get('process_gold_papers') for d in log_summary.values()
              if d.get('process_gold_papers')] if dd != 'MISSING'])
    ))

    print('Gold PDFs success/fail/skip parse to TETML: {}/{}/{}'.format(
        sum([dd.get('parse_pdf_to_tetml').get('success') for dd in
             [d.get('process_gold_papers') for d in log_summary.values()
              if d.get('process_gold_papers')] if dd != 'MISSING']),
        sum([dd.get('parse_pdf_to_tetml').get('fail') for dd in
             [d.get('process_gold_papers') for d in log_summary.values()
              if d.get('process_gold_papers')] if dd != 'MISSING']),
        sum([dd.get('parse_pdf_to_tetml').get('skip') for dd in
             [d.get('process_gold_papers') for d in log_summary.values()
              if d.get('process_gold_papers')] if dd != 'MISSING'])
    ))

    print('Gold TETML success/fail/skip Table Extractor: {}/{}/{}'.format(
        sum([dd.get('extract_tables_from_tetml').get('success') for dd in
             [d.get('process_gold_papers') for d in log_summary.values()
              if d.get('process_gold_papers')] if dd != 'MISSING']),
        sum([dd.get('extract_tables_from_tetml').get('fail') for dd in
             [d.get('process_gold_papers') for d in log_summary.values()
              if d.get('process_gold_papers')] if dd != 'MISSING']),
        sum([dd.get('extract_tables_from_tetml').get('skip') for dd in
             [d.get('process_gold_papers') for d in log_summary.values()
              if d.get('process_gold_papers')] if dd != 'MISSING'])
    ))

    print('Gold candidate/usable tables: {}/{}'.format(
        sum([d.get('extract_gold_tables').get('num_candidate') for d in log_summary.values() if d.get('process_gold_papers')]),
        sum([d.get('extract_gold_tables').get('num_relevant') for d in log_summary.values() if d.get('process_gold_papers')])
    ))

    print('Relevant source papers: {}'.format(
        sum([d.get('relevant_source_papers') for d in log_summary.values() if d.get('relevant_source_papers')])
    ))
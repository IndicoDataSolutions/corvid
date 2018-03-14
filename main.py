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

from bs4 import BeautifulSoup

from corvid.table_extraction.table_extractor import TetmlTableExtractor
from corvid.util.files import is_url_working, read_one_json_from_es, \
    fetch_one_pdf_from_s3
from corvid.util.tetml import parse_one_pdf
from config import DATASETS_JSON, ES_PROD_URL, S3_PDFS_URL, PDF_DIR, \
    TET_BIN_PATH, TETML_DIR, convert_paper_id_to_s3_filename, \
    convert_paper_id_to_es_endpoint

CAPTION_SEARCH_WINDOW = 3

if __name__ == '__main__':
    with open(DATASETS_JSON, 'r') as f_datasets:
        datasets = json.load(f_datasets)

    # verify external dependencies
    assert is_url_working(ES_PROD_URL)
    assert is_url_working(S3_PDFS_URL)
    assert os.path.exists(TET_BIN_PATH)

    log_summary = {}

    for dataset in datasets:
        dataset_name = dataset.get('name')
        dataset_aliases = dataset.get('aliases')
        dataset_paper_id = dataset.get('paper_id')

        # logging
        log_summary[dataset_name] = {
            'dataset_paper_id': None,
            'fetch_dataset_paper_json_from_es': None,
            'fetch_pdf_from_s3': {
                'success': 0,
                'fail': 0
            },
            'parse_pdf_to_tetml': {
                'success': 0,
                'fail': 0
            },
            'extract_tables_from_tetml': {
                'success': 0,
                'fail': 0
            }
        }

        if not dataset_paper_id:
            log_summary[dataset_name]['dataset_paper_id'] = 'FAIL'
            continue

        # fetch dataset paper JSON & find paper_ids that cite this dataset
        try:
            dataset_paper_json = read_one_json_from_es(
                es_url=ES_PROD_URL,
                paper_id=dataset_paper_id,
                convert_paper_id_to_es_endpoint=convert_paper_id_to_es_endpoint)
            relevant_paper_ids = dataset_paper_json.get('citedBy')
        except Exception as e:
            print(e)
            log_summary[dataset_name]['fetch_dataset_paper_json_from_es'] = 'FAIL'
            continue

        dataset_tables = []
        for paper_id in relevant_paper_ids:
            # fetch PDFs of relevant papers
            try:
                pdf_path = fetch_one_pdf_from_s3(
                    s3_url=S3_PDFS_URL,
                    paper_id=paper_id,
                    out_dir=PDF_DIR,
                    convert_paper_id_to_s3_filename=convert_paper_id_to_s3_filename,
                    is_overwrite=False)
                log_summary[dataset_name]['fetch_pdf_from_s3']['success'] += 1
            except Exception as e:
                print(e)
                log_summary[dataset_name]['fetch_pdf_from_s3']['fail'] += 1
                continue

            # parse each PDF to TETML
            try:
                tetml_path = parse_one_pdf(tet_path=TET_BIN_PATH,
                                           pdf_path=pdf_path,
                                           out_dir=TETML_DIR,
                                           is_overwrite=False)
                log_summary[dataset_name]['parse_pdf_to_tetml']['success'] += 1
            except Exception as e:
                print(e)
                log_summary[dataset_name]['parse_pdf_to_tetml']['fail'] += 1
                continue

            # extract tables from TETML
            try:
                with open(tetml_path, 'r') as f_tetml:
                    tables = TetmlTableExtractor.extract_tables(
                        tetml=BeautifulSoup(f_tetml),
                        caption_search_window=CAPTION_SEARCH_WINDOW)
                    dataset_tables.extend(tables)
                log_summary[dataset_name]['extract_tables_from_tetml']['success'] += 1
            except Exception as e:
                print(e)
                log_summary[dataset_name]['extract_tables_from_tetml']['fail'] += 1
                continue

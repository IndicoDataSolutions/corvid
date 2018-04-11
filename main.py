"""

"""

import os

from typing import List, Dict

import json

try:
    import cPickle as pickle
except:
    import pickle

import numpy as np

# pipeline functions
from collections import namedtuple
GoldTableRecord = namedtuple('GoldTableRecord', ['paper_id', 'caption_id'])
from corvid.pipeline.retrieve_tables_from_paper_id import retrieve_tables_from_paper_id, POSSIBLE_EXCEPTIONS

# resource managers
from corvid.pipeline.paper_fetcher import ElasticSearchJSONPaperFetcher, S3PDFPaperFetcher
from corvid.pipeline.pdf_parser import PDFParser, TetmlPDFParser, OmnipagePDFParser

# table extraction
from corvid.table_extraction.table_extractor import TableExtractor, TetmlTableExtractor, OmnipageTableExtractor

# table aggregation
from corvid.table_aggregation.schema_matcher import ColNameSchemaMatcher
from corvid.table_aggregation.schema_matcher import ColValueSchemaMatcher
from corvid.table_aggregation.evaluate import evaluate

# types
from elasticsearch import Elasticsearch
from corvid.types.table import Table
from corvid.types.dataset import Dataset

# util
from corvid.util.strings import remove_non_alphanumeric

# paths
from config import DATASETS_JSON, DATASETS_PICKLE, DATASETS_LOG,\
    ES_PROD_URL, ES_PAPER_DOC_TYPE, ES_PAPER_INDEX, JSON_DIR, get_references, \
    S3_PDFS_BUCKET, PDF_DIR, \
    TET_BIN_PATH, TETML_XML_DIR, TETML_PICKLE_DIR, \
    OMNIPAGE_BIN_PATH, OMNIPAGE_XML_DIR, OMNIPAGE_PICKLE_DIR, \
    AGGREGATE_PICKLE, AGGREGATE_LOG\


def is_match_gold_table_record(candidate_gold_table: Table,
                               gold_table_record: GoldTableRecord) -> bool:
    """
    Note: `caption_id` refers to the text at beginning of captions that
          identifies the specific table within a paper.  for example,
          'table iv' or 'table 2'
    """

    is_correct_paper = candidate_gold_table.paper_id == gold_table_record.paper_id

    normalized_gold_table_caption = remove_non_alphanumeric(candidate_gold_table.caption).lower()
    normalized_caption_id = remove_non_alphanumeric(gold_table_record.caption_id).lower()
    is_starts_with_caption_id = normalized_gold_table_caption.startswith(normalized_caption_id)

    # return is_correct_paper and is_starts_with_caption_id
    return is_starts_with_caption_id


def get_source_paper_ids(es_client: Elasticsearch,
                         gold_table: Table,
                         dataset: Dataset) -> List[str]:
    return get_references(es=es_client, paper_id=gold_table.paper_id)


# initialize resources
schema_matcher = ColNameSchemaMatcher()
schema_matcher2 = ColValueSchemaMatcher()

json_fetcher = ElasticSearchJSONPaperFetcher(host_url=ES_PROD_URL,
                                             index=ES_PAPER_INDEX,
                                             doc_type=ES_PAPER_DOC_TYPE,
                                             target_dir=JSON_DIR)
# pdf_fetcher = S3PDFPaperFetcher(bucket=S3_PDFS_BUCKET, target_dir=PDF_DIR)
# tetml_pdf_parser = TetmlPDFParser(tet_bin_path=TET_BIN_PATH,
#                                   target_dir=TETML_XML_DIR)
# omnipage_pdf_parser = OmnipagePDFParser(omnipage_bin_path=OMNIPAGE_BIN_PATH,
#                                         target_dir=OMNIPAGE_XML_DIR)
# tetml_table_extractor = TetmlTableExtractor(target_dir=TETML_PICKLE_DIR)
# omnipage_table_extractor = OmnipageTableExtractor(target_dir=OMNIPAGE_PICKLE_DIR)


def build_datasets(pdf_parser: PDFParser, table_extractor: TableExtractor) -> List[Dataset]:
    with open(DATASETS_JSON, 'r') as f_datasets:
        dataset_records = json.load(f_datasets)

    log_datasets = {
        'num_dataset_without_paper_id': 0,
        'num_dataset_without_gold_tables': 0,
        'num_gold_record_success': 0,
        'num_gold_record_known_exceptions': {exception.__name__: 0 for exception in POSSIBLE_EXCEPTIONS},
        'num_gold_record_unknown_exceptions': 0
    }

    datasets = []
    for dataset_record in dataset_records:

        # required fields for dataset record include `paper_id` and `gold_table_ids`
        dataset_paper_id = dataset_record.get('paper_id')
        if not dataset_paper_id:
            log_datasets['num_dataset_without_paper_id'] += 1
            continue

        gold_table_records = dataset_record.get('gold_tables')
        if not gold_table_records or len(gold_table_records) < 1:
            log_datasets['num_dataset_without_gold_tables'] += 1
            continue

        # TODO: BUG.  exits at first gold record failure. needs to be closer to gold loop
        matched_gold_tables = []

        gold_table_records = [
            GoldTableRecord(paper_id=gold_table_record.get('paper_id'),
                            caption_id=gold_table_record.get('caption_id'))
            for gold_table_record in gold_table_records
        ]

        for gold_table_record in gold_table_records:

            try:
                # note: may return fewer than number indicated in `gold_table_records`
                candidate_gold_tables = retrieve_tables_from_paper_id(
                    paper_id=gold_table_record.paper_id,
                    pdf_fetcher=pdf_fetcher,
                    pdf_parser=pdf_parser,
                    table_extractor=table_extractor
                )

                for candidate_gold_table in candidate_gold_tables:
                    if is_match_gold_table_record(candidate_gold_table,
                                                  gold_table_record):
                        matched_gold_tables.append(candidate_gold_table)

                dataset = Dataset(name=remove_non_alphanumeric(dataset_record.get('name')),
                                  paper_id=dataset_paper_id,
                                  aliases=[remove_non_alphanumeric(alias) for alias in dataset_record.get('aliases')] if dataset_record.get('aliases') else [],
                                  gold_tables=matched_gold_tables)

                datasets.append(dataset)
                log_datasets['num_gold_record_success'] += 1

            except Exception as e:
                print(e)
                if type(e) not in POSSIBLE_EXCEPTIONS:
                    log_datasets['num_gold_record_unknown_exceptions'] += 1
                else:
                    for i, exception_type in enumerate(POSSIBLE_EXCEPTIONS):
                        if type(e) == exception_type:
                            log_datasets['num_gold_record_known_exceptions'][type(e).__name__] += 1
                continue

    with open(DATASETS_PICKLE, 'wb') as f_datasets_pickle:
        pickle.dump(datasets, f_datasets_pickle)
    with open(DATASETS_LOG, 'w') as f_log_datasets:
        json.dump(log_datasets, f_log_datasets)

    return datasets


def build_aggregates(datasets) -> Dict:
    # with open(DATASETS_PICKLE, 'rb') as f_datasets_pickle:
    #     datasets = pickle.load(f_datasets_pickle)

    log_sources = {
        'num_missing_source_paper_ids': 0,
        'num_source_table_success': 0,
        'num_source_table_known_exceptions': {exception.__name__: 0 for exception in POSSIBLE_EXCEPTIONS},
        'num_source_table_unknown_exceptions': 0
    }

    all_results = {}
    for dataset in datasets:

        results_per_dataset = []
        for gold_table in dataset.gold_tables:

            # TODO: refactor to not rely on logic from `config.py`
            # TODO: temp restrict to only papers cited by gold paper
            source_paper_ids = get_source_paper_ids(es_client=json_fetcher.es,
                                                    gold_table=gold_table,
                                                    dataset=dataset)
            if len(source_paper_ids) < 1:
                log_sources['num_missing_source_paper_ids'] += 1
                continue

            source_tables = []
            for source_paper_id in source_paper_ids:
                try:
                    # source_tables.extend(retrieve_tables_from_paper_id(
                    #     paper_id=source_paper_id,
                    #     pdf_fetcher=pdf_fetcher,
                    #     pdf_parser=pdf_parser,
                    #     table_extractor=table_extractor
                    # ))
                    with open('data/omnipage/pickle/{}.pickle'.format(source_paper_id), 'rb') as f_source_paper:
                        source_tables.extend(pickle.load(f_source_paper))

                    log_sources['num_source_table_success'] += 1
                except Exception as e:
                    if type(e) not in POSSIBLE_EXCEPTIONS:
                        log_sources['num_source_table_unknown_exceptions'] += 1
                    else:
                        for i, exception_type in enumerate(POSSIBLE_EXCEPTIONS):
                            if type(e) == exception_type:
                                log_sources['num_source_table_known_exceptions'][type(e).__name__] += 1
                    continue

            pairwise_mappings = schema_matcher2.map_tables(
                tables=source_tables,
                target_schema=gold_table
            )
            aggregate_table = schema_matcher2.aggregate_tables(
                pairwise_mappings=pairwise_mappings,
                target_schema=gold_table
            )

            # a single result is for a dataset-gold pair
            results_per_dataset.append({
                'num_source_papers': len(source_paper_ids),
                'pairwise_mappings': pairwise_mappings,
                'gold_table': gold_table,
                'pred_table': aggregate_table,
                'score': evaluate(gold_table=gold_table,
                                  pred_table=aggregate_table)
            })

        all_results.update({dataset.paper_id: results_per_dataset})

    # save results for all gold tables under this dataset
    with open(AGGREGATE_PICKLE, 'wb') as f_results:
        pickle.dump(all_results, f_results)
    with open(AGGREGATE_LOG, 'w') as f_log_sources:
        json.dump(log_sources, f_log_sources)

    return all_results


if __name__ == '__main__':

    # tetml_datasets = build_datasets(tetml_pdf_parser, tetml_table_extractor)
    # omnipage_datasets = build_datasets(omnipage_pdf_parser, omnipage_table_extractor)
    with open('data/datasets.pickle', 'rb') as f_datasets:
        omnipage_datasets = pickle.load(f_datasets)

    # tetml_results = build_aggregates(tetml_pdf_parser, tetml_table_extractor)
    omnipage_results = build_aggregates(datasets=omnipage_datasets)


    #print(np.mean([result.get('score').get('cell_level_recall') for results in tetml_results.values() for result in results]))
    #print(np.mean([result.get('score').get('row_level_recall') for results in tetml_results.values() for result in results]))

    print(np.mean([result.get('score').get('cell_level_recall') for results in omnipage_results.values() for result in results]))
    print(np.mean([result.get('score').get('row_level_recall') for results in omnipage_results.values() for result in results]))
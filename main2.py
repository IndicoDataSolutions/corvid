"""

"""

import os

from typing import List

import json

try:
    import cPickle as pickle
except:
    import pickle


# pipeline functions
from collections import namedtuple
GoldTableRecord = namedtuple('GoldTableRecord', ['paper_id', 'caption_id'])
from corvid.pipeline.extract_tables_from_paper_id import extract_tables_from_paper_id, POSSIBLE_EXCEPTIONS

# resource managers
from corvid.pipeline.paper_fetcher import ElasticSearchJSONPaperFetcher, S3PDFPaperFetcher
from corvid.pipeline.pdf_parser import TetmlPDFParser

# table aggregation
from corvid.table_aggregation.schema_matcher import ColNameSchemaMatcher
from corvid.table_aggregation.evaluate import evaluate

# types
from elasticsearch import Elasticsearch
from corvid.types.table import Table
from corvid.types.dataset import Dataset

# util
from corvid.util.strings import remove_non_alphanumeric

# paths
from config import DATASETS_JSON, \
    ES_PROD_URL, ES_PAPER_DOC_TYPE, ES_PAPER_INDEX, JSON_DIR, get_references, \
    S3_PDFS_BUCKET, PDF_DIR, \
    TET_BIN_PATH, TETML_DIR, \
    PICKLE_DIR, \
    AGGREGATION_PICKLE_DIR


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


if __name__ == '__main__':
    with open(DATASETS_JSON, 'r') as f_datasets:
        dataset_records = json.load(f_datasets)

    # initialize resources
    schema_matcher = ColNameSchemaMatcher()
    json_fetcher = ElasticSearchJSONPaperFetcher(host_url=ES_PROD_URL,
                                                 index=ES_PAPER_INDEX,
                                                 doc_type=ES_PAPER_DOC_TYPE,
                                                 target_dir=JSON_DIR)
    pdf_fetcher = S3PDFPaperFetcher(bucket=S3_PDFS_BUCKET, target_dir=PDF_DIR)
    pdf_parser = TetmlPDFParser(tet_bin_path=TET_BIN_PATH, target_dir=TETML_DIR)

    log_datasets = {
        'num_dataset_without_paper_id': 0,
        'num_dataset_without_gold_tables': 0,
        'num_gold_record_success': 0,
        'num_gold_record_known_exceptions': {exception.__name__: 0 for exception in POSSIBLE_EXCEPTIONS},
        'num_gold_record_unknown_exceptions': 0
    }

    all_results = {}
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
                candidate_gold_tables = extract_tables_from_paper_id(
                    paper_id=gold_table_record.paper_id,
                    pdf_fetcher=pdf_fetcher,
                    pdf_parser=pdf_parser,
                    target_table_dir=PICKLE_DIR
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

        results_per_dataset = []
        for gold_table in dataset.gold_tables:

            # TODO: refactor to not rely on logic from `config.py`
            # TODO: temp restrict to only papers cited by gold paper
            source_paper_ids = get_source_paper_ids(es_client=json_fetcher.es,
                                                    gold_table=gold_table,
                                                    dataset=dataset)

            log_sources = {
                'num_known_exceptions': {exception.__name__: 0 for exception in POSSIBLE_EXCEPTIONS},
                'num_unknown_exceptions': 0
            }
            source_tables = []
            for source_paper_id in source_paper_ids:
                try:
                    source_tables.extend(extract_tables_from_paper_id(
                        paper_id=source_paper_id,
                        pdf_fetcher=pdf_fetcher,
                        pdf_parser=pdf_parser,
                        target_table_dir=PICKLE_DIR
                    ))
                except Exception as e:
                    if type(e) not in POSSIBLE_EXCEPTIONS:
                        log_sources['num_unknown_exceptions'] += 1
                    else:
                        for i, exception_type in enumerate(POSSIBLE_EXCEPTIONS):
                            if type(e) == exception_type:
                                log_sources['num_known_exceptions'][type(e).__name__] += 1
                    continue

            pairwise_mappings = schema_matcher.map_tables(
                tables=source_tables,
                target_schema=gold_table
            )
            aggregate_table = schema_matcher.aggregate_tables(
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
            }.update(log_sources))

        # save results for all gold tables under this dataset
        agg_pickle_path = '{}.pickle'.format(os.path.join(AGGREGATION_PICKLE_DIR, dataset_paper_id))
        with open(agg_pickle_path, 'wb') as f_results:
            pickle.dump(results_per_dataset, f_results)

        all_results.update({dataset_paper_id: results_per_dataset})


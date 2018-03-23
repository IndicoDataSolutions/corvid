"""



"""

import json

# pipeline functions
from corvid.pipeline.create_dataset_from_json_record import create_dataset_from_json_record, GoldTableRecord, POSSIBLE_EXCEPTIONS
from corvid.pipeline.extract_tables_from_paper_id import extract_tables_from_paper_id

# resource managers
from corvid.pipeline.paper_fetcher import ElasticSearchJSONPaperFetcher, S3PDFPaperFetcher
from corvid.pipeline.pdf_parser import TetmlPDFParser

# table aggregation
from corvid.table_aggregation.schema_matcher import ColNameSchemaMatcher

# util
from corvid.util.strings import remove_non_alphanumeric

# paths
from config import DATASETS_JSON, \
    ES_PROD_URL, ES_PAPER_DOC_TYPE, ES_PAPER_INDEX, \
    S3_PDFS_BUCKET, PDF_DIR, \
    TET_BIN_PATH, TETML_DIR, \
    PICKLE_DIR

def main():
    with open(DATASETS_JSON, 'r') as f_datasets:
        dataset_records = json.load(f_datasets)

    # initialize resources

    # es_client.get(id=author_id, index='author', doc_type='author')['_source']
    # es_client = default_es_client(ES_PROD_URL)

    schema_matcher = ColNameSchemaMatcher()
    pdf_fetcher = S3PDFPaperFetcher(bucket=S3_PDFS_BUCKET, target_dir=PDF_DIR)
    pdf_parser = TetmlPDFParser(tet_bin_path=TET_BIN_PATH, target_dir=TETML_DIR)

    log_datasets = {
        'num_dataset_without_paper_id': 0,
        'num_dataset_without_gold_tables': 0,
        'num_known_exceptions': [[exception.__name__, 0] for exception in POSSIBLE_EXCEPTIONS],
        'num_unknown_exceptions': 0
    }

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

        try:
            dataset = create_dataset_from_json_record(
                name=remove_non_alphanumeric(dataset_record.get('name')),
                aliases=[remove_non_alphanumeric(alias) for alias in dataset_record.get('aliases')] if dataset_record.get('aliases') else [],
                paper_id=dataset_paper_id,
                gold_table_records=[GoldTableRecord(paper_id=gold_table_record.get('paper_id'),
                                                    caption_id=gold_table_record.get('caption_id'))
                                    for gold_table_record in gold_table_records],
                pdf_fetcher=pdf_fetcher,
                pdf_parser=pdf_parser,
                target_table_dir=PICKLE_DIR
            )
        except Exception as e:
            if type(e) not in POSSIBLE_EXCEPTIONS:
                log_datasets['num_unknown_exceptions'] += 1
            else:
                for i, exception_type in enumerate(POSSIBLE_EXCEPTIONS):
                    if type(e) == exception_type:
                        log_datasets['num_known_exceptions'][i][-1] += 1
            continue


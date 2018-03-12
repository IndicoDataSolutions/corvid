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

import json

from corvid.util.files import is_url_working, read_one_json_from_es, \
    fetch_one_pdf_from_s3
from config import DATASETS_JSON, ES_PROD_URL, S3_PDFS_URL, PDF_DIR

if __name__ == '__main__':
    with open(DATASETS_JSON, 'r') as f:
        datasets = json.load(f)

    assert is_url_working(ES_PROD_URL)
    for dataset in datasets:
        # find relevant papers using citations
        dataset_paper_json = read_one_json_from_es(
            es_url=ES_PROD_URL,
            paper_id=dataset.get('paper_id'))
        relevant_paper_ids = dataset_paper_json.get('citedBy')

        # fetch pdfs of relevant papers & extract tables
        tables = []
        for paper_id in relevant_paper_ids:
            fetch_one_pdf_from_s3(s3_url=S3_PDFS_URL,
                                  paper_id=relevant_paper_ids,
                                  out_dir=PDF_DIR,
                                  is_overwrite=False)
            

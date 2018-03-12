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

from config import DATASETS_JSON

if __name__ == '__main__':
    with open(DATASETS_JSON, 'r') as f:
        datasets = json.load(f)

    for dataset in datasets:
        tables = []

        papers = find_relevant_papers(dataset)

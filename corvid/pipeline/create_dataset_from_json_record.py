"""

Handles processing of a dataset record given a JSON input

"""

from typing import List

from collections import namedtuple

from corvid.types.dataset import Dataset
from corvid.types.table import Table

from corvid.util.strings import remove_non_alphanumeric

from corvid.pipeline.extract_tables_from_paper_id import extract_tables_from_paper_id, POSSIBLE_EXCEPTIONS

GoldTableRecord = namedtuple('GoldTableRecord', ['paper_id', 'caption_id'])


def create_dataset_from_json_record(name: str,
                                    aliases: List[str],
                                    paper_id: str,
                                    gold_table_records: List[GoldTableRecord],
                                    pdf_fetcher,
                                    pdf_parser,
                                    target_table_dir) -> Dataset:
    """
    A single dataset JSON record will, at least, have the fields:
    {
        "name": "mnist",
        "aliases": [
            "handwritten digits",
            "modified institute of standards and technology"
        ],
        "paper_id": "id_of_paper_publishing_this_dataset",
        "gold_table_records": [
            {
                "paper_id": "id_of_paper_containing_gold_table",
                "caption_id": "table vii"
            },
            ...
        ]
    }

    Note:  if one of these fields is missing (e.g. dataset missing paper_id),
           the Dataset object will still be created.
    """

    matched_gold_tables = []

    for gold_table_record in gold_table_records:
        # note: may return fewer than number indicated in `gold_table_records`
        candidate_gold_tables = extract_tables_from_paper_id(
            paper_id=gold_table_record.paper_id,
            pdf_fetcher=pdf_fetcher,
            pdf_parser=pdf_parser,
            target_table_dir=target_table_dir
        )

        for candidate_gold_table in candidate_gold_tables:
            if is_match_gold_table_record(candidate_gold_table,
                                          gold_table_record):
                matched_gold_tables.append(candidate_gold_table)

    return Dataset(name=name,
                   paper_id=paper_id,
                   aliases=aliases,
                   gold_tables=matched_gold_tables)



def is_match_gold_table_record(candidate_gold_table: Table,
                               gold_table_record: GoldTableRecord) -> bool:
    """
    Note: `caption_id` refers to the text at beginning of captions that
          identifies the specific table within a paper.  for example,
          'table iv' or 'table 2'
    """

    is_correct_paper = candidate_gold_table.paper_id == gold_table_record.paper_id
    is_starts_with_caption_id = remove_non_alphanumeric(candidate_gold_table.caption).lower().startswith(gold_table_record.caption_id)

    return is_correct_paper and is_starts_with_caption_id

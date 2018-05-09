"""


"""

from typing import List

from corvid.table.table import Table


# TODO
def predict_table_relevance(table: Table) -> float:
    return float('inf')


# TODO
def filter_tables(tables: List[Table], min_relevance: float) -> List[Table]:
    return [table for table in tables
            if predict_table_relevance(table) > min_relevance]

"""


"""

from typing import List

from corvid.semantic_table.table import Table


class TableFilter(object):
    def filter(self, tables: List[Table]) -> List[Table]:
        raise NotImplementedError


class SemanticTableFilter(TableFilter):
    def __init__(self, threshold: float):
        self.threshold = threshold

    def filter(self, tables: List[Table]) -> List[Table]:
        return [table for table in tables
                if self._predict_relevance(table) > self.threshold]

    # TODO: baseline implementation is to perform a regex over cells for known names
    def _predict_relevance(self, table: Table) -> float:
        pass

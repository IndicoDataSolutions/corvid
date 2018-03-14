"""



"""

from corvid.types.table import Table
from typing import List, Tuple


class PairwiseMapping(object):
    """
    """

    def __init__(self, table1: Table, table2: Table, score: float,
                 column_mappings: List[Tuple[int, int]]):
        self.table1 = table1
        self.table2 = table2
        self.score = score
        self.column_mappings = column_mappings

    def __eq__(self, other: 'PairwiseMapping') -> bool:
        return self.score == other.score

    def __lt__(self, other: 'PairwiseMapping') -> bool:
        return self.score < other.score

    def __gt__(self, other: 'PairwiseMapping') -> bool:
        return self.column_mappings > other.score


    def __le__(self, other: 'PairwiseMapping') -> bool:
        return self.score <= other.score


    def __ge__(self, other: 'PairwiseMapping') -> bool:
        return self.column_mappings >= other.score
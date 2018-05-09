"""



"""

from typing import List, Tuple

from corvid.table.table import Table


class PairwiseMapping(object):
    """
    Class stores output from a schema matcher between a pair of
    tables along with references to the two tables.
    Output includes a list of column mappings between the two tables
    and a cumulative score indicating how well the the two tables map
    """

    def __init__(self, table1: Table, table2: Table,
                 column_mappings: List[Tuple[int, int]],
                 score: float = 0.0):
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

import unittest

from corvid.semantic_table.table import Table
from corvid.table_aggregation.pairwise_mapping import PairwiseMapping


class TestPairwiseMapping(unittest.TestCase):
    def setUp(self):
        self.table1 = Table()
        self.table2 = Table()
        self.pairwise_mapping = PairwiseMapping(self.table1, self.table2, score=1.0,
                                           column_mappings=list())

    def test_eq(self):
        pairwise_mapping = PairwiseMapping(self.table1, self.table2, score=1.0,
                                           column_mappings=list())
        self.assertTrue(self.pairwise_mapping == pairwise_mapping)
        pairwise_mapping.score = 0.5
        self.assertFalse(self.pairwise_mapping == pairwise_mapping)
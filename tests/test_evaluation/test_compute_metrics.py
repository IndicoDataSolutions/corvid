"""


"""

import unittest

from corvid.types.table import Token, Cell, Table
from corvid.evaluation.compute_metrics import compute_metrics


class TestComputeMetrics(unittest.TestCase):
    def setUp(self):
        self.gold_table = Table(cells=[
            Cell(tokens=[Token(text='Model')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='EM')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='F1')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='CNN')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='35')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='15')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='RNN')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='75')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='50')], rowspan=1, colspan=1)
        ], nrow=3, ncol=3)

        self.pred_table = Table(cells=[
            Cell(tokens=[Token(text='Model')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='EM')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='F1')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='CNN')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='35')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='15')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='RNN')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='75')], rowspan=1, colspan=1),
            Cell(tokens=[Token(text='50')], rowspan=1, colspan=1)
        ], nrow=3, ncol=3)

    def test_compute_metrics(self):
        self.assertDictEqual(
            compute_metrics(self.gold_table, self.pred_table),
            {
                'row_level_recall': 1.0,
                'cell_level_recall': 1.0
            }
        )

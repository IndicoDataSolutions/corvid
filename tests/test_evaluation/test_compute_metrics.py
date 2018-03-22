"""


"""

import unittest

from corvid.table_aggregation.compute_metrics import count_matching_cells, \
    row_level_recall, cell_level_recall, compute_metrics
from corvid.types.table import Token, Cell, Table


class TestComputeMetrics(unittest.TestCase):
    def setUp(self):
        """
        gold:
            subject, header1, header2
            x, 1, 2
            y, 3, 4
            z, 5, 6
        """
        self.gold_table = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='subject')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='x')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='y')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='4')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='z')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='5')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='6')], rowspan=1, colspan=1)
            ], nrow=4, ncol=3)

        self.gold_table_empty = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='subject')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header2')], rowspan=1, colspan=1)
            ], nrow=1, ncol=3)

        self.pred_table_perfect = self.gold_table

        self.pred_table_empty = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='subject')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header2')], rowspan=1, colspan=1)
            ], nrow=1, ncol=3)

        self.pred_table_permute_rows = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='subject')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='z')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='5')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='6')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='y')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='4')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='x')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1)
            ], nrow=4, ncol=3)

        self.pred_table_extra_rows = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='subject')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='x')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='y')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='4')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='z')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='5')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='6')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='w')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='7')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='8')], rowspan=1, colspan=1)
            ], nrow=5, ncol=3)

        self.pred_table_missing_rows = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='subject')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='x')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='y')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='4')], rowspan=1, colspan=1)
            ], nrow=3, ncol=3)

        self.pred_table_partial_credit = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='subject')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='x')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='y')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='4')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='4')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='z')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1)
            ], nrow=4, ncol=3)

    def test_count_matching_cells(self):
        self.assertEqual(count_matching_cells(
            row1=[
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1)
            ],
            row2=[
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1)
            ]), 3.0)

        self.assertEqual(count_matching_cells(
            row1=[
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1)
            ],
            row2=[
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1)
            ]), 1.0)

    def test_row_level_recall(self):
        self.assertEqual(
            row_level_recall(gold_table=self.gold_table,
                             pred_table=self.pred_table_perfect), 1.0)

        with self.assertRaises(Exception):
            row_level_recall(gold_table=self.gold_table_empty,
                             pred_table=self.pred_table_perfect)

        self.assertEqual(
            row_level_recall(gold_table=self.gold_table,
                             pred_table=self.pred_table_empty), 0.0)

        self.assertEqual(
            row_level_recall(gold_table=self.gold_table,
                             pred_table=self.pred_table_permute_rows), 1.0)

        self.assertEqual(
            row_level_recall(gold_table=self.gold_table,
                             pred_table=self.pred_table_extra_rows), 1.0)

        self.assertEqual(
            row_level_recall(gold_table=self.gold_table,
                             pred_table=self.pred_table_missing_rows), 2 / 3)

        self.assertEqual(
            row_level_recall(gold_table=self.gold_table,
                             pred_table=self.pred_table_partial_credit), 0.0)

    def test_cell_level_recall(self):
        self.assertEqual(
            cell_level_recall(gold_table=self.gold_table,
                              pred_table=self.pred_table_perfect), 1.0)

        with self.assertRaises(Exception):
            cell_level_recall(gold_table=self.gold_table_empty,
                              pred_table=self.pred_table_perfect)

        self.assertEqual(
            cell_level_recall(gold_table=self.gold_table,
                              pred_table=self.pred_table_permute_rows), 1.0)

        self.assertEqual(
            cell_level_recall(gold_table=self.gold_table,
                              pred_table=self.pred_table_extra_rows), 1.0)

        self.assertEqual(
            cell_level_recall(gold_table=self.gold_table,
                              pred_table=self.pred_table_missing_rows), 2 / 3)

        self.assertEqual(
            cell_level_recall(gold_table=self.gold_table,
                              pred_table=self.pred_table_partial_credit), 1 / 3)

    def test_compute_metrics(self):
        pred_table_missing_header = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='x')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='y')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='4')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='z')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='5')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='6')], rowspan=1, colspan=1)
            ], nrow=3, ncol=3)

        with self.assertRaises(Exception):
            compute_metrics(gold_table=self.gold_table,
                            pred_table=pred_table_missing_header)

        self.assertEqual(
            cell_level_recall(gold_table=self.gold_table,
                              pred_table=self.pred_table_empty), 0.0)

        pred_table_permuted_header = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='subject')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='header1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='x')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='y')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='4')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='3')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='z')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='6')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='5')], rowspan=1, colspan=1)
            ], nrow=4, ncol=3)

        with self.assertRaises(Exception):
            compute_metrics(gold_table=self.gold_table,
                            pred_table=pred_table_permuted_header)

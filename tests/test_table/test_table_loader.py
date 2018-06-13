"""



"""

import unittest

from corvid.table.table_loader import Cell, CellLoader, Table, \
    TableLoader


class TestCellLoader(unittest.TestCase):
    def setUp(self):
        self.cell_loader = CellLoader(cell_type=Cell)

    def test_from_json(self):
        cell = self.cell_loader.from_json(json={
            'tokens': ['a', 'b'],
            'index_topleft_row': 1,
            'index_topleft_col': 2,
            'rowspan': 3,
            'colspan': 4
        })
        self.assertListEqual(cell.tokens, ['a', 'b'])
        self.assertEqual(cell.index_topleft_row, 1)
        self.assertEqual(cell.index_topleft_col, 2)
        self.assertEqual(cell.rowspan, 3)
        self.assertEqual(cell.colspan, 4)


class TestTableLoader(unittest.TestCase):
    def setUp(self):
        self.cell_loader = CellLoader(cell_type=Cell)
        self.table_loader = TableLoader(table_type=Table,
                                        cell_loader=self.cell_loader)

    def test_from_json(self):
        table = self.table_loader.from_json(json={
            'cells': [
                {
                    'tokens': ['a'],
                    'index_topleft_row': 0,
                    'index_topleft_col': 0,
                    'rowspan': 2,
                    'colspan': 2
                },
                {
                    'tokens': ['b'],
                    'index_topleft_row': 0,
                    'index_topleft_col': 2,
                    'rowspan': 1,
                    'colspan': 2
                },
                {
                    'tokens': ['c'],
                    'index_topleft_row': 1,
                    'index_topleft_col': 2,
                    'rowspan': 1,
                    'colspan': 2
                },
                {
                    'tokens': ['d'],
                    'index_topleft_row': 2,
                    'index_topleft_col': 0,
                    'rowspan': 2,
                    'colspan': 4
                }
            ],
            'nrow': 4,
            'ncol': 4
        })
        self.assertEqual(str(table).replace(' ', ''),
                         'a\ta\tb\tb\na\ta\tc\tc\nd\td\td\td\nd\td\td\td')

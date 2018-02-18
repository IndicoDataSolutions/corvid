"""


"""

import unittest

from corvid.types.table import Cell, Table


class TestBox(unittest.TestCase):
    def setUp(self):
        self.box = Cell(tokens='hi', rowspan=1, colspan=1)

    def test_str(self):
        self.assertEqual(str(self.box), 'hi')


class TestTable(unittest.TestCase):
    def setUp(self):
        self.a = Cell(tokens='a', rowspan=1, colspan=1)
        self.b = Cell(tokens='b', rowspan=1, colspan=1)
        self.c = Cell(tokens='c', rowspan=1, colspan=1)
        self.d = Cell(tokens='d', rowspan=1, colspan=1)
        self.e = Cell(tokens='e', rowspan=1, colspan=1)
        self.f = Cell(tokens='f', rowspan=1, colspan=1)
        self.easy_table = Table(cells=[self.a, self.b, self.c,
                                       self.d, self.e, self.f],
                                nrow=2, ncol=3, paper_id='abc', page_num=0,
                                caption='hi this is caption')

        self.hard_table = Table(cells=[
            Cell(tokens='', rowspan=2, colspan=2),
            Cell(tokens='C', rowspan=1, colspan=2),
            Cell(tokens='C:1', rowspan=1, colspan=1),
            Cell(tokens='C:2', rowspan=1, colspan=1),
            Cell(tokens='R', rowspan=3, colspan=1),
            Cell(tokens='R:1', rowspan=1, colspan=1),
            Cell(tokens='a', rowspan=1, colspan=1),
            Cell(tokens='b', rowspan=1, colspan=1),
            Cell(tokens='R:2', rowspan=1, colspan=1),
            Cell(tokens='c', rowspan=1, colspan=1),
            Cell(tokens='d', rowspan=1, colspan=1),
            Cell(tokens='R:3', rowspan=1, colspan=1),
            Cell(tokens='e', rowspan=1, colspan=1),
            Cell(tokens='f', rowspan=1, colspan=1)
        ], nrow=5, ncol=4, paper_id='abc', page_num=0,
            caption='hi this is caption')

    def test_improper_table(self):
        with self.assertRaises(Exception):
            # misspecified nrow or ncol
            Table(cells=[Cell(tokens='a', rowspan=1, colspan=1),
                         Cell(tokens='b', rowspan=1, colspan=1),
                         Cell(tokens='c', rowspan=1, colspan=1),
                         Cell(tokens='d', rowspan=1, colspan=1)],
                  nrow=2, ncol=1, paper_id='', page_num=0, caption='')
            Table(cells=[Cell(tokens='a', rowspan=1, colspan=1),
                         Cell(tokens='b', rowspan=1, colspan=1),
                         Cell(tokens='c', rowspan=1, colspan=1),
                         Cell(tokens='d', rowspan=1, colspan=1)],
                  nrow=1, ncol=2, paper_id='', page_num=0, caption='')

            # not enough cells to fill out table
            Table(cells=[Cell(tokens='a', rowspan=1, colspan=1),
                         Cell(tokens='b', rowspan=1, colspan=1),
                         Cell(tokens='c', rowspan=1, colspan=1)],
                  nrow=2, ncol=2, paper_id='', page_num=0, caption='')
            Table(cells=[Cell(tokens='a', rowspan=1, colspan=1),
                         Cell(tokens='b', rowspan=1, colspan=1)],
                  nrow=2, ncol=2, paper_id='', page_num=0, caption='')

            # cell juts out of table boundaries
            Table(cells=[Cell(tokens='a', rowspan=1, colspan=2)],
                  nrow=1, ncol=1, paper_id='', page_num=0, caption='')

    def test_shape_properties(self):
        self.assertEqual(self.easy_table.nrow, 2)
        self.assertEqual(self.easy_table.ncol, 3)
        self.assertEqual(self.easy_table.dim, (2, 3))
        self.assertEqual(self.hard_table.nrow, 5)
        self.assertEqual(self.hard_table.ncol, 4)
        self.assertEqual(self.hard_table.dim, (5, 4))

    def test_grid_indexing(self):
        # single elements
        self.assertEqual(self.easy_table[0, 0], self.a)
        self.assertEqual(self.easy_table[-1, -1], self.f)
        # full row
        self.assertListEqual(self.easy_table[0, :], [self.a, self.b, self.c])
        self.assertListEqual(self.easy_table[1, :], [self.d, self.e, self.f])
        # partial row
        self.assertListEqual(self.easy_table[0, 1:], [self.b, self.c])
        self.assertListEqual(self.easy_table[0, :2], [self.a, self.b])
        self.assertListEqual(self.easy_table[0, 1:2], [self.b])
        # full column
        self.assertListEqual(self.easy_table[:, 0], [self.a, self.d])
        # partial column
        self.assertListEqual(self.easy_table[1:, 0], [self.d])
        self.assertListEqual(self.easy_table[:1, 0], [self.a])
        self.assertListEqual(self.easy_table[1:2, 0], [self.d])
        # full subgrid
        subgrid = self.easy_table[:, :]
        self.assertListEqual(subgrid[0], [self.a, self.b, self.c])
        self.assertListEqual(subgrid[1], [self.d, self.e, self.f])
        # partial subgrid
        subgrid = self.easy_table[1:2, 1:2]
        self.assertListEqual(subgrid[0], [self.e])
        subgrid = self.easy_table[1:, 1:]
        self.assertListEqual(subgrid[0], [self.e, self.f])
        subgrid = self.easy_table[:2, :2]
        self.assertListEqual(subgrid[0], [self.a, self.b])
        self.assertListEqual(subgrid[1], [self.d, self.e])

        # repetition for multicol/row cells
        self.assertEqual([cell.text for cell in self.hard_table[0, :]],
                         ['', '', 'C', 'C'])
        self.assertEqual([cell.text for cell in self.hard_table[:, 0]],
                         ['', '', 'R', 'R', 'R'])

    def test_list_indexing(self):
        self.assertEqual(self.easy_table[0], self.a)
        self.assertEqual(self.easy_table[-1], self.f)
        self.assertListEqual(self.easy_table[:2], [self.a, self.b])
        self.assertListEqual(self.easy_table[4:], [self.e, self.f])
        self.assertListEqual(self.easy_table[:], [self.a, self.b, self.c,
                                                  self.d, self.e, self.f])

    def test_str(self):
        self.assertEqual(str(self.easy_table), 'a\tb\tc\nd\te\tf')
        s = '\t\tC\tC\n\t\tC:1\tC:2\nR\tR:1\ta\tb\nR\tR:2\tc\td\nR\tR:3\te\tf'
        self.assertEqual(str(self.hard_table).replace(' ', ''), s)

    def test_transpose(self):
        transposed_grid = self.easy_table.transpose()
        self.assertListEqual([cell.text for cell in transposed_grid[0, :]],
                             [self.a.tokens, self.d.tokens])
        self.assertListEqual([cell.text for cell in transposed_grid[1, :]],
                             [self.b.tokens, self.e.tokens])
        self.assertListEqual([cell.text for cell in transposed_grid[2, :]],
                             [self.c.tokens, self.f.tokens])

        transposed_grid = self.hard_table.transpose()
        self.assertEqual(transposed_grid.cells[4].rowspan, 1)
        self.assertEqual(transposed_grid.cells[4].colspan, 3)
        s = '\t\tR\tR\tR\n\t\tR:1\tR:2\tR:3\nC\tC:1\ta\tc\te\nC\tC:2\tb\td\tf'
        self.assertEqual(str(transposed_grid).replace(' ', ''), s)

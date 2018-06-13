"""


"""

import unittest

import numpy as np
from numpy.testing import assert_array_equal

from corvid.table.table import Cell, Table


class TestCell(unittest.TestCase):
    def setUp(self):
        self.cell = Cell(tokens=['hi', 'bye'],
                         index_topleft_row=1, index_topleft_col=2,
                         rowspan=2, colspan=2)

    def test_str(self):
        self.assertEqual(str(self.cell), 'hi bye')

    def test_indices(self):
        self.assertListEqual(self.cell.indices,
                             [(1, 2), (1, 3), (2, 2), (2, 3)])


class TestTable(unittest.TestCase):
    def setUp(self):
        """
        >     |       |        C       |
        >     |       |   C:1  |  C:2  |
        >  R  |  R:1  |    a   |   b   |
        >  R  |  R:2  |    c   |   d   |
        >  R  |  R:3  |    e   |   f   |
        """
        self.a = Cell(tokens=[''], index_topleft_row=0,
                      index_topleft_col=0, rowspan=2, colspan=2)
        self.b = Cell(tokens=['C'], index_topleft_row=0,
                      index_topleft_col=2, rowspan=1, colspan=2)
        self.c = Cell(tokens=['C:1'], index_topleft_row=1,
                      index_topleft_col=2, rowspan=1, colspan=1)
        self.d = Cell(tokens=['C:2'], index_topleft_row=1,
                      index_topleft_col=3, rowspan=1, colspan=1)
        self.e = Cell(tokens=['R'], index_topleft_row=2,
                      index_topleft_col=0, rowspan=3, colspan=1)
        self.f = Cell(tokens=['R:1'], index_topleft_row=2,
                      index_topleft_col=1, rowspan=1, colspan=1)
        self.g = Cell(tokens=['R:2'], index_topleft_row=3,
                      index_topleft_col=1, rowspan=1, colspan=1)
        self.h = Cell(tokens=['R:3'], index_topleft_row=4,
                      index_topleft_col=1, rowspan=1, colspan=1)
        self.i = Cell(tokens=['a'], index_topleft_row=2,
                      index_topleft_col=2, rowspan=1, colspan=1)
        self.j = Cell(tokens=['b'], index_topleft_row=2,
                      index_topleft_col=3, rowspan=1, colspan=1)
        self.k = Cell(tokens=['c'], index_topleft_row=3,
                      index_topleft_col=2, rowspan=1, colspan=1)
        self.l = Cell(tokens=['d'], index_topleft_row=3,
                      index_topleft_col=3, rowspan=1, colspan=1)
        self.m = Cell(tokens=['e'], index_topleft_row=4,
                      index_topleft_col=2, rowspan=1, colspan=1)
        self.n = Cell(tokens=['f'], index_topleft_row=4,
                      index_topleft_col=3, rowspan=1, colspan=1)

        self.single_cell_table = Table(grid=[
            [self.a, self.a],
            [self.a, self.a]
        ])

        self.full_table = Table(grid=[
            [self.a, self.a, self.b, self.b],
            [self.a, self.a, self.c, self.d],
            [self.e, self.f, self.i, self.j],
            [self.e, self.g, self.k, self.l],
            [self.e, self.h, self.m, self.n]
        ])

    def test_multiple_create_inputs(self):
        with self.assertRaises(AssertionError):
            Table(grid=[[]], cells=[])

    def test_create_from_grid(self):
        self.assertListEqual(Table(grid=np.array([[self.a, self.a],
                                                  [self.a, self.a]])).cells,
                             [self.a])
        self.assertListEqual(
            Table(grid=[[self.a, self.a, self.b, self.b],
                        [self.a, self.a, self.c, self.d],
                        [self.e, self.f, self.i, self.j],
                        [self.e, self.g, self.k, self.l],
                        [self.e, self.h, self.m, self.n]]).cells,
            [self.a, self.b, self.c, self.d,
             self.e, self.f, self.i, self.j,
             self.g, self.k, self.l, self.h,
             self.m, self.n])

    def test_create_from_cells(self):
        table = Table(cells=[self.a], nrow=2, ncol=2)
        assert_array_equal(table.grid, self.single_cell_table.grid)
        table = Table(cells=[self.a, self.b, self.c, self.d,
                             self.e, self.f, self.i, self.j,
                             self.g, self.k, self.l, self.h,
                             self.m, self.n], nrow=5, ncol=4)
        assert_array_equal(table.grid, self.full_table.grid)

    def test_empty_table(self):
        with self.assertRaises(AssertionError):
            Table(cells=[], nrow=0, ncol=0)

        with self.assertRaises(AssertionError):
            Table()

        with self.assertRaises(AssertionError):
            Table(grid=[[]])

        with self.assertRaises(AssertionError):
            Table(grid=[])

    def test_improper_table(self):
        # misspecified nrow or ncol raises IndexError
        with self.assertRaises(IndexError):
            Table(cells=[Cell(tokens=['a'], index_topleft_row=0,
                              index_topleft_col=0, rowspan=1, colspan=1),
                         Cell(tokens=['b'], index_topleft_row=0,
                              index_topleft_col=1, rowspan=1, colspan=1),
                         Cell(tokens=['c'], index_topleft_row=1,
                              index_topleft_col=0, rowspan=1, colspan=1),
                         Cell(tokens=['d'], index_topleft_row=1,
                              index_topleft_col=1, rowspan=1, colspan=1)],
                  nrow=2, ncol=1)

        with self.assertRaises(IndexError):
            Table(cells=[Cell(tokens=['a'], index_topleft_row=0,
                              index_topleft_col=0, rowspan=1, colspan=1),
                         Cell(tokens=['b'], index_topleft_row=0,
                              index_topleft_col=1, rowspan=1, colspan=1),
                         Cell(tokens=['c'], index_topleft_row=1,
                              index_topleft_col=0, rowspan=1, colspan=1),
                         Cell(tokens=['d'], index_topleft_row=1,
                              index_topleft_col=1, rowspan=1, colspan=1)],
                  nrow=1, ncol=2)

        # not enough cells to fill out table
        with self.assertRaises(ValueError):
            Table(cells=[Cell(tokens=['a'], index_topleft_row=0,
                              index_topleft_col=0, rowspan=1, colspan=1),
                         Cell(tokens=['b'], index_topleft_row=0,
                              index_topleft_col=1, rowspan=1, colspan=1),
                         Cell(tokens=['c'], index_topleft_row=1,
                              index_topleft_col=0, rowspan=1, colspan=1)],
                  nrow=2, ncol=2)

        with self.assertRaises(ValueError):
            Table(cells=[Cell(tokens=['a'], index_topleft_row=0,
                              index_topleft_col=0, rowspan=1, colspan=1),
                         Cell(tokens=['b'], index_topleft_row=0,
                              index_topleft_col=1, rowspan=1, colspan=1)],
                  nrow=2, ncol=2)

        # cell protrudes out of table boundaries
        with self.assertRaises(IndexError):
            Table(cells=[Cell(tokens=['a'], index_topleft_row=0,
                              index_topleft_col=0, rowspan=1, colspan=2)],
                  nrow=1, ncol=1)

    def test_shape_properties(self):
        self.assertEqual(self.full_table.nrow, 5)
        self.assertEqual(self.full_table.ncol, 4)
        self.assertEqual(self.full_table.shape, (5, 4))

    def test_grid_indexing(self):
        # multiple single-element indices access same Cell
        self.assertEqual(self.full_table[0, 0], self.a)
        self.assertEqual(self.full_table[1, 1], self.a)
        self.assertEqual(self.full_table[-1, -1], self.n)

        # row indexing returns a List of Cells
        self.assertListEqual(self.full_table[0, 1:], [self.a, self.b, self.b])
        self.assertListEqual(self.full_table[-1, :3], [self.e, self.h, self.m])
        self.assertListEqual(self.full_table[-1, 3:4], [self.n])

        # col indexing returns a List of Cells
        self.assertListEqual(self.full_table[1:4, 0], [self.a, self.e, self.e])
        self.assertListEqual(self.full_table[:3, -1], [self.b, self.d, self.j])
        self.assertListEqual(self.full_table[3:4, -1], [self.l])

        # subgrid indexing raises Exception
        with self.assertRaises(IndexError):
            self.full_table[1:3, 1:3]

    def test_cell_indexing(self):
        # each index identifies a unique Cell (disregarding cell span)
        self.assertEqual(self.full_table[0], self.a)
        self.assertEqual(self.full_table[1], self.b)
        self.assertEqual(self.full_table[2], self.c)
        self.assertEqual(self.full_table[3], self.d)
        self.assertEqual(self.full_table[-1], self.n)

        # slice indexing returns a List of Cells
        self.assertListEqual(self.full_table[1:4], [self.b, self.c, self.d])

    def test_str(self):
        t = '\t\tC\tC\n\t\tC:1\tC:2\nR\tR:1\ta\tb\nR\tR:2\tc\td\nR\tR:3\te\tf'
        self.assertEqual(str(self.full_table).replace(' ', ''), t)

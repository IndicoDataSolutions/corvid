"""


"""

import unittest

from extract_empirical_results.types.table import Box, Grid, Cell, Table


class TestBox(unittest.TestCase):
    def setUp(self):
        self.box = Box(text='hi')

    def test_str(self):
        self.assertEqual(str(self.box), 'hi')


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.a = Box(text='a')
        self.b = Box(text='b')
        self.c = Box(text='c')
        self.d = Box(text='d')
        self.e = Box(text='e')
        self.f = Box(text='f')
        self.grid = Grid(grid=[
            [self.a, self.b, self.c],
            [self.d, self.e, self.f]
        ])

    def test_improper_grid(self):
        with self.assertRaises(Exception):
            Grid(grid=[
                [Box(text='a'), Box(text='b')],
                [Box(text='c')]
            ])

    def test_shape_properties(self):
        self.assertEqual(self.grid.nrow, 2)
        self.assertEqual(self.grid.ncol, 3)
        self.assertEqual(self.grid.dim, (2, 3))

    def test_indexing(self):
        # single elements
        self.assertEqual(self.grid[0, 0], self.a)
        self.assertEqual(self.grid[-1, -1], self.f)
        # full row
        self.assertListEqual(self.grid[0, :], [self.a, self.b, self.c])
        self.assertListEqual(self.grid[1, :], [self.d, self.e, self.f])
        # partial row
        self.assertListEqual(self.grid[0, 1:], [self.b, self.c])
        self.assertListEqual(self.grid[0, :2], [self.a, self.b])
        self.assertListEqual(self.grid[0, 1:2], [self.b])
        # full column
        self.assertListEqual(self.grid[:, 0], [self.a, self.d])
        # partial column
        self.assertListEqual(self.grid[1:, 0], [self.d])
        self.assertListEqual(self.grid[:1, 0], [self.a])
        self.assertListEqual(self.grid[1:2, 0], [self.d])
        # full subgrid
        subgrid = self.grid[:, :]
        self.assertListEqual(subgrid[0], [self.a, self.b, self.c])
        self.assertListEqual(subgrid[1], [self.d, self.e, self.f])
        # partial subgrid
        subgrid = self.grid[1:2, 1:2]
        self.assertListEqual(subgrid[0], [self.e])
        subgrid = self.grid[1:, 1:]
        self.assertListEqual(subgrid[0], [self.e, self.f])
        subgrid = self.grid[:2, :2]
        self.assertListEqual(subgrid[0], [self.a, self.b])
        self.assertListEqual(subgrid[1], [self.d, self.e])

    def test_str(self):
        self.assertEqual(str(self.grid), 'a\tb\tc\nd\te\tf')

    def test_transpose(self):
        transposed_grid = self.grid.transpose()
        self.assertListEqual(transposed_grid[0, :], [self.a, self.d])
        self.assertListEqual(transposed_grid[1, :], [self.b, self.e])
        self.assertListEqual(transposed_grid[2, :], [self.c, self.f])

    def test_flatten(self):
        self.assertListEqual(self.grid.flatten(row_wise=True),
                             [self.a, self.b, self.c, self.d, self.e, self.f])
        self.assertListEqual(self.grid.flatten(row_wise=False),
                             [self.a, self.d, self.b, self.e, self.c, self.f])


class TestCell(unittest.TestCase):
    def setUp(self):
        self.grid = Grid(grid=[
            [Box(text='x'), Box(text='x'), Box(text='o')],
            [Box(text='x'), Box(text='x'), Box(text='o')]
        ])
        self.cell = Cell(source_grid=self.grid,
                         idx_col_start=0, idx_col_end=2,
                         idx_row_start=0, idx_row_end=2)

    def test_improper_cell(self):
        with self.assertRaises(Exception):
            Cell(source_grid=self.grid,
                 idx_col_start=1, idx_col_end=3,
                 idx_row_start=1, idx_row_end=3)

    def test_str(self):
        self.assertEqual(str(self.cell), 'x')


class TestTable(unittest.TestCase):
    def setUp(self):
        self.grid = Grid(grid=[
            [Box(text=''), Box(text=''), Box(text='C'), Box(text='C')],
            [Box(text=''), Box(text=''), Box(text='C:1'), Box(text='C:2')],
            [Box(text='R'), Box(text='R:1'), Box(text='a'), Box(text='b')],
            [Box(text='R'), Box(text='R:2'), Box(text='c'), Box(text='d')],
            [Box(text='R'), Box(text='R:3'), Box(text='e'), Box(text='f')]
        ])
        self.cell_empty = Cell(source_grid=self.grid,
                               idx_col_start=0, idx_col_end=2,
                               idx_row_start=0, idx_row_end=2)
        self.cell_colhead = Cell(source_grid=self.grid,
                                 idx_col_start=2, idx_col_end=4,
                                 idx_row_start=0, idx_row_end=1)
        self.cell_rowhead = Cell(source_grid=self.grid,
                                 idx_col_start=0, idx_col_end=1,
                                 idx_row_start=2, idx_row_end=5)
        self.table = Table(grid=self.grid,
                           cells=[self.cell_empty,
                                  self.cell_colhead,
                                  self.cell_rowhead],
                           table_id=0,
                           paper_id=0,
                           page_num=0,
                           caption='This is a caption.')

    def test_str(self):
        s = '\t\tC\tC\n\t\tC:1\tC:2\nR\tR:1\ta\tb\nR\tR:2\tc\td\nR\tR:3\te\tf'
        self.assertEqual(str(self.table).replace(' ', ''), s)

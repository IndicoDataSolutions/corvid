"""


"""

import unittest

import numpy as np

from corvid.types.table import Box, Token, Cell, Table, EMPTY_CAPTION


class TestCell(unittest.TestCase):
    def setUp(self):
        self.cell = Cell(tokens=[
            Token(text='hi',
                  bounding_box=Box(llx=-1.0, lly=-0.5, urx=1.0, ury=1.0)),
            Token(text='bye',
                  bounding_box=Box(llx=1.5, lly=-0.5, urx=2.5, ury=1.5))
        ], rowspan=1, colspan=1)

    def test_str(self):
        self.assertEqual(str(self.cell), 'hi bye')

    def test_compute_bounding_box(self):
        box = self.cell.bounding_box
        self.assertEqual(box.ll.x, -1.0)
        self.assertEqual(box.ll.y, -0.5)
        self.assertEqual(box.ur.x, 2.5)
        self.assertEqual(box.ur.y, 1.5)


class TestTable(unittest.TestCase):
    def setUp(self):
        self.a = Cell(tokens=[Token(text='a')], rowspan=1, colspan=1)
        self.b = Cell(tokens=[Token(text='b')], rowspan=1, colspan=1)
        self.c = Cell(tokens=[Token(text='c')], rowspan=1, colspan=1)
        self.d = Cell(tokens=[Token(text='d')], rowspan=1, colspan=1)
        self.e = Cell(tokens=[Token(text='e')], rowspan=1, colspan=1)
        self.f = Cell(tokens=[Token(text='f')], rowspan=1, colspan=1)
        self.easy_table = Table(caption='hi this is caption')
        self.easy_table.grid = np.array([
            [self.a, self.b, self.c],
            [self.d, self.e, self.f]
        ])

        self.hard_table = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='')], rowspan=2, colspan=2),
                Cell(tokens=[Token(text='C')], rowspan=1, colspan=2),
                Cell(tokens=[Token(text='C:1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='C:2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='R')], rowspan=3, colspan=1),
                Cell(tokens=[Token(text='R:1')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='a')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='b')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='R:2')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='c')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='d')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='R:3')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='e')], rowspan=1, colspan=1),
                Cell(tokens=[Token(text='f')], rowspan=1, colspan=1)
            ], nrow=5, ncol=4, paper_id='abc', page_num=0,
            caption='hi this is caption')

    def test_create_from_grid(self):
        self.assertEqual(Table.create_from_grid(grid=[
            [self.a, self.b, self.c],
            [self.d, self.e, self.f]
        ]), self.easy_table)

    # TODO
    def test_create_from_cells(self):
        pass

    def test_improper_table(self):
        # misspecified nrow or ncol
        with self.assertRaises(Exception):
            Table.create_from_cells(
                cells=[Cell(tokens=[Token(text='a')], rowspan=1, colspan=1),
                       Cell(tokens=[Token(text='b')], rowspan=1, colspan=1),
                       Cell(tokens=[Token(text='c')], rowspan=1, colspan=1),
                       Cell(tokens=[Token(text='d')], rowspan=1, colspan=1)],
                nrow=2, ncol=1, paper_id='', page_num=0, caption='')

        with self.assertRaises(Exception):
            Table.create_from_cells(
                cells=[Cell(tokens=[Token(text='a')], rowspan=1, colspan=1),
                       Cell(tokens=[Token(text='b')], rowspan=1, colspan=1),
                       Cell(tokens=[Token(text='c')], rowspan=1, colspan=1),
                       Cell(tokens=[Token(text='d')], rowspan=1, colspan=1)],
                nrow=1, ncol=2, paper_id='', page_num=0, caption='')

        # not enough cells to fill out table
        with self.assertRaises(Exception):
            Table.create_from_cells(
                cells=[Cell(tokens=[Token(text='a')], rowspan=1, colspan=1),
                       Cell(tokens=[Token(text='b')], rowspan=1, colspan=1),
                       Cell(tokens=[Token(text='c')], rowspan=1, colspan=1)],
                nrow=2, ncol=2, paper_id='', page_num=0, caption='')

        with self.assertRaises(Exception):
            Table.create_from_cells(
                cells=[Cell(tokens=[Token(text='a')], rowspan=1, colspan=1),
                       Cell(tokens=[Token(text='b')], rowspan=1, colspan=1)],
                nrow=2, ncol=2, paper_id='', page_num=0, caption='')

        # cell juts out of table boundaries
        with self.assertRaises(Exception):
            Table.create_from_cells(
                cells=[Cell(tokens=[Token(text='a')], rowspan=1, colspan=2)],
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
        self.assertEqual(self.easy_table, self.easy_table[:, :])
        # partial subgrid
        self.assertEqual(self.easy_table[1:2, 1:2],
                         Table.create_from_grid(grid=[[self.e]]))
        self.assertEqual(self.easy_table[1:, 1:],
                         Table.create_from_grid(grid=[[self.e, self.f]]))
        self.assertEqual(self.easy_table[:2, :2],
                         Table.create_from_grid(grid=[[self.a, self.b],
                                                      [self.d, self.e]]))

    def test_str(self):
        self.assertEqual(str(self.easy_table),
                         'a\tb\tc\nd\te\tf' + '\n' + 'hi this is caption')
        t = '\t\tC\tC\n\t\tC:1\tC:2\nR\tR:1\ta\tb\nR\tR:2\tc\td\nR\tR:3\te\tf'
        c = 'hithisiscaption'
        self.assertEqual(str(self.hard_table).replace(' ', ''), t + '\n' + c)

    def test_insert_row(self):
        x = Cell(tokens=[Token(text='x')], rowspan=1, colspan=1)
        y = Cell(tokens=[Token(text='y')], rowspan=1, colspan=1)
        z = Cell(tokens=[Token(text='z')], rowspan=1, colspan=1)
        self.assertEqual(self.easy_table.insert_row(index=1, row=[x, y, z]),
                         Table.create_from_grid(grid=[
                             [self.a, self.b, self.c],
                             [x, y, z],
                             [self.d, self.e, self.f]
                         ]))
        with self.assertRaises(Exception):
            self.easy_table.insert_row(index=1, row=[x, y])

    def test_insert_column(self):
        x = Cell(tokens=[Token(text='x')], rowspan=1, colspan=1)
        y = Cell(tokens=[Token(text='y')], rowspan=1, colspan=1)
        self.assertEqual(self.easy_table.insert_column(index=1, column=[x, y]),
                         Table.create_from_grid(grid=[
                             [self.a, x, self.b, self.c],
                             [self.d, y, self.e, self.f]
                         ]))
        with self.assertRaises(Exception):
            self.easy_table.insert_column(index=1, column=[x, y, y])

    def test_delete_row(self):
        self.assertEqual(self.easy_table.delete_row(index=1),
                         Table.create_from_grid(grid=[
                             [self.a, self.b, self.c]
                         ]))

    def test_delete_column(self):
        self.assertEqual(self.easy_table.delete_column(index=1),
                         Table.create_from_grid(grid=[
                             [self.a, self.c],
                             [self.d, self.f]
                         ]))

    def test_compute_bounding_box(self):
        table = Table.create_from_cells(
            cells=[
                Cell(tokens=[Token(text='e')], rowspan=1, colspan=1,
                     bounding_box=Box(llx=-1.0, lly=-0.5, urx=1.0, ury=1.0)),
                Cell(tokens=[Token(text='e')], rowspan=1, colspan=1,
                     bounding_box=Box(llx=1.5, lly=-0.5, urx=2.5, ury=1.5))
            ],
            nrow=1, ncol=2, paper_id='abc', page_num=0,
            caption='hi this is caption')
        box = table.bounding_box
        self.assertEqual(box.ll.x, -1.0)
        self.assertEqual(box.ll.y, -0.5)
        self.assertEqual(box.ur.x, 2.5)
        self.assertEqual(box.ur.y, 1.5)

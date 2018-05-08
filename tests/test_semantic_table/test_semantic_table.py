"""


"""

import unittest

from numpy.testing import assert_array_equal

from corvid.semantic_table.semantic_table import Cell, Table, SemanticTable


class TestSemanticTable(unittest.TestCase):
    def setUp(self):
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

        self.table = Table(grid=[
            [self.a, self.a, self.b, self.b],
            [self.a, self.a, self.c, self.d],
            [self.e, self.f, self.i, self.j],
            [self.e, self.g, self.k, self.l],
            [self.e, self.h, self.m, self.n]
        ])

        self.semantic_table = SemanticTable(raw_table=self.table)

    def test_insert_rows(self):
        index_insert = 1
        x = Cell(tokens=['x'], index_topleft_row=index_insert, index_topleft_col=0, rowspan=1, colspan=1)
        y = Cell(tokens=['y'], index_topleft_row=index_insert, index_topleft_col=1, rowspan=1, colspan=1)
        z = Cell(tokens=['z'], index_topleft_row=index_insert, index_topleft_col=2, rowspan=1, colspan=1)
        w = Cell(tokens=['w'], index_topleft_row=index_insert, index_topleft_col=3, rowspan=1, colspan=1)
        self.semantic_table.insert_row(index=index_insert, row=[x, y, z, w])
        self.assertEqual(str(self.semantic_table.normalized_table).replace(' ', ''),
                         '\t\tC\tC\nx\ty\tz\tw\n\t\tC:1\tC:2\nR\tR:1\ta\tb\nR\tR:2\tc\td\nR\tR:3\te\tf')

    #
    #
    #     # with self.assertRaises(Exception):
    #     #     self.semantic_table.insert_row(index=1, row=[x, y, y])
    #
    # def test_insert_column(self):
    #     x = Cell(tokens=[Token(text='x')], rowspan=1, colspan=1)
    #     y = Cell(tokens=[Token(text='y')], rowspan=1, colspan=1)
    #     self.assertEqual(self.table.insert_column(index=1, column=[x, y]),
    #                      Table.create_from_grid(grid=[
    #                          [self.a, x, self.b, self.c],
    #                          [self.d, y, self.e, self.f]
    #                      ]))
    #     with self.assertRaises(Exception):
    #         self.table.insert_column(index=1, column=[x, y, y])
    #
    # def test_delete_row(self):
    #     self.assertEqual(self.table.delete_row(index=1),
    #                      Table.create_from_grid(grid=[
    #                          [self.a, self.b, self.c]
    #                      ]))
    #
    # def test_delete_column(self):
    #     self.assertEqual(self.table.delete_column(index=1),
    #                      Table.create_from_grid(grid=[
    #                          [self.a, self.c],
    #                          [self.d, self.f]
    #                      ]))
    #
    # def test_append_left(self):
    #     self.assertEqual(
    #         self.table.append_left(other=Table.create_from_grid(
    #             grid=[[self.f, self.b, self.d],
    #                   [self.c, self.e, self.a]])),
    #         Table.create_from_grid(
    #             grid=[[self.f, self.b, self.d, self.a, self.b, self.c],
    #                   [self.c, self.e, self.a, self.d, self.e, self.f]])
    #     )
    #
    # def test_append_right(self):
    #     self.assertEqual(
    #         self.table.append_right(other=Table.create_from_grid(
    #             grid=[[self.f, self.b, self.d],
    #                   [self.c, self.e, self.a]])),
    #         Table.create_from_grid(
    #             grid=[[self.a, self.b, self.c, self.f, self.b, self.d],
    #                   [self.d, self.e, self.f, self.c, self.e, self.a]])
    #     )
    #
    # def test_append_top(self):
    #     self.assertEqual(
    #         self.table.append_top(other=Table.create_from_grid(
    #             grid=[[self.f, self.b, self.d],
    #                   [self.c, self.e, self.a]])),
    #         Table.create_from_grid(
    #             grid=[[self.f, self.b, self.d],
    #                   [self.c, self.e, self.a],
    #                   [self.a, self.b, self.c],
    #                   [self.d, self.e, self.f]])
    #     )
    #
    # def test_append_bottom(self):
    #     self.assertEqual(
    #         self.table.append_bottom(other=Table.create_from_grid(
    #             grid=[[self.f, self.b, self.d],
    #                   [self.c, self.e, self.a]])),
    #         Table.create_from_grid(
    #             grid=[[self.a, self.b, self.c],
    #                   [self.d, self.e, self.f],
    #                   [self.f, self.b, self.d],
    #                   [self.c, self.e, self.a]])
    #     )
    #
    # def test_compute_bounding_box(self):
    #     table = Table.create_from_cells(
    #         cells=[
    #             Cell(tokens=[Token(text='e')], rowspan=1, colspan=1,
    #                  bounding_box=Box(llx=-1.0, lly=-0.5, urx=1.0, ury=1.0)),
    #             Cell(tokens=[Token(text='e')], rowspan=1, colspan=1,
    #                  bounding_box=Box(llx=1.5, lly=-0.5, urx=2.5, ury=1.5))
    #         ],
    #         nrow=1, ncol=2, paper_id='abc', page_num=0,
    #         caption='hi this is caption')
    #     box = table.bounding_box
    #     self.assertEqual(box.ll.x, -1.0)
    #     self.assertEqual(box.ll.y, -0.5)
    #     self.assertEqual(box.ur.x, 2.5)
    #     self.assertEqual(box.ur.y, 1.5)

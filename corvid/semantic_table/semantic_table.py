"""

Given a raw Table, the SemanticTable will learn its underlying semantics
which is represented as a relational table where:

 - "Values" in the raw Table induce rows (instances) of the relational table
 - "Labels" in the raw Table induce cols (schema) of the relational table

For example, a raw Table

>        |          header          |
>        |  col1  |  col2  |  col3  |
>  row1  |    a   |    b   |    c   |
>  row2  |    d   |    e   |    f   |

"""

from typing import List, Tuple, Union

import numpy as np
import re

from functools import reduce

from corvid.table.table import Table, Cell
from corvid.util.strings import format_grid, count_digits, \
    remove_non_alphanumeric, is_like_citation


class NormalizationError(Exception):
    pass


class SemanticTable(object):
    VALID_LABELS = ['metric', 'method', 'dataset', 'value', 'other', 'empty']
    ROW_LABELS = ['method']
    COL_LABELS = ['metric', 'dataset']

    def __init__(self, raw_table: Table):
        self.raw_table = raw_table
        self.normalized_table = self.normalize_table(raw_table=self.raw_table)

    def normalize_table(self, raw_table: Table) -> Table:

        # (1)
        index_topmost_value_row, index_leftmost_value_col = \
            self._classify_cells(table=raw_table)

        # (2)
        new_table = self._standardize_cell_sizes(table=raw_table)

        # (3)
        new_table = self._merge_label_cells(
            table=new_table,
            index_topmost_value_row=index_topmost_value_row,
            index_leftmost_value_col=index_leftmost_value_col)

        return new_table

    def _classify_cells(self, table: Table) -> Tuple[int, int]:
        """
        Some thoughts:
        Nearly all tables should have bottom-right cell be a VALUE.

        Can perform decently if assume a Table is split into a VALUE rectangle
        and a LABEL "L" shape.  The problem is thus finding the right-most LABEL
        column, and the bottom-most LABEL row.  Every cell to the bottom/right
        of that is a VALUE.

        In this case, there are 4 mistakes we can make:
        (1) a LABEL column is classified as VALUE
        (2) a VALUE column is classified as LABEL
        (3) a LABEL row is classified as VALUE
        (4) a VALUE row is classified as LABEL

        For a downstream task of aggregating tables based on column matching,
        (1) is not a big deal:  subject columns don't count towards performance,
        and worse-case, the column doesn't get matched.
        (2) is worse because one fewer column can worsen the matching.
        (3) is sort of bad because losing a header string can worsen the matching,
        but this can probably be made up via value-based matching.
        (4) is very bad because losing a row means losing a possible matching
        when evaluating recall.

        As such, cell classification is incentivized to aggressively classify
        columns as VALUES.  Unclear, but probably also incentivized to
        aggressively classify rows as VALUES.
        """

        index_value_cell_rows = []
        index_value_cell_cols = []

        # (1) first pass to do easy ones
        for cell in table.cells:

            text = remove_non_alphanumeric(str(cell))

            # RULE 0:  EMPTY CELLS ARE IGNORED
            if text == '':
                cell.label = 'EMPTY'

            # RULE 1:  MULTIROW/COL CELLS ARE PROBABLY LABELS
            elif cell.rowspan > 1 or cell.colspan > 1:
                cell.label = 'LABEL'

            # RULE 2:  A CELL WITH 100% TEXT IS PROBABLY A LABEL
            elif count_digits(text) == 0:
                cell.label = 'LABEL'

            # RULE 3:  A CELL WITH >50% DIGITS IS PROBABLY A VALUE
            elif count_digits(text) / len(text) > 0.5:
                cell.label = 'VALUE'
                index_value_cell_rows.append(cell.index_topleft_row)
                index_value_cell_cols.append(cell.index_topleft_col)

            else:
                cell.label = 'UNKNOWN'

        # (2) second pass to use neighborhood info
        index_leftmost_value_col = table.ncol - 1
        while index_leftmost_value_col >= 0:
            if all([table[i, index_leftmost_value_col].label != 'VALUE'
                    for i in range(table.nrow)]):
                break
            index_leftmost_value_col -= 1
        index_leftmost_value_col += 1

        index_topmost_value_row = table.nrow - 1
        while index_topmost_value_row >= 0:
            if all([table[index_topmost_value_row, j].label != 'VALUE'
                    for j in range(table.ncol)]):
                break
            index_topmost_value_row -= 1
        index_topmost_value_row += 1

        if index_leftmost_value_col == table.ncol and index_topmost_value_row == table.nrow:
            raise NormalizationError('No values in this table')

        # re-label top-left quadrant
        for i in range(index_topmost_value_row):
            for j in range(index_leftmost_value_col):
                table[i, j].label = 'EMPTY'

        # re-label top-right quadrant
        for i in range(index_topmost_value_row):
            for j in range(index_leftmost_value_col, table.ncol):
                table[i, j].label = 'LABEL'

        # re-label bottom-left quadrant
        for i in range(index_topmost_value_row, table.nrow):
            for j in range(index_leftmost_value_col):
                table[i, j].label = 'LABEL'

        # re-label bottom-right quadrant
        for i in range(index_topmost_value_row, table.nrow):
            for j in range(index_leftmost_value_col, table.ncol):
                table[i, j].label = 'VALUE'

        return index_topmost_value_row, index_leftmost_value_col

    def _standardize_cell_sizes(self, table: Table) -> Table:
        """Creates new cells for multispan cells"""
        new_cells = []
        for raw_cell in table.cells:
            for i, j in raw_cell.indices:
                new_cell = Cell(tokens=raw_cell.tokens,
                                index_topleft_row=i,
                                index_topleft_col=j,
                                rowspan=1,
                                colspan=1)
                new_cell.label = raw_cell.label
                new_cells.append(new_cell)
        return Table(cells=new_cells,
                     nrow=table.nrow,
                     ncol=table.ncol)

    def _merge_label_cells(self, table: Table,
                           index_topmost_value_row: int,
                           index_leftmost_value_col: int) -> Table:
        """
        Some thoughts:
        Typically, the top-left quadrant cells are a super-label to describe
        the label columns in the bottom-left quadrant.  Hence, when merging
        'LABEL' cells, we'll prioritize merging rows over merging columns.
        """
        new_table = table

        if index_leftmost_value_col > 1:
            # decrement col indices of all cells to the right of collapsed cols
            for i in range(new_table.nrow):
                for j in range(index_leftmost_value_col, new_table.ncol):
                    new_table[i, j].index_topleft_col -= \
                        (index_leftmost_value_col - 1)

            # overwrite leftmost col cell tokens
            for i in range(new_table.nrow):
                new_table[i, 0].tokens = reduce(
                    lambda l1, l2: l1 + l2,
                    [c.tokens for c in new_table[i, :index_leftmost_value_col]]
                )

            # delete collapsed cols (except for leftmost)
            new_grid = np.delete(new_table.grid,
                                 list(range(1, index_leftmost_value_col)),
                                 axis=1)
            new_table = Table(grid=new_grid.tolist())

        if index_topmost_value_row > 1:
            # decrement row indices of all cells below the collapsed rows
            for i in range(index_topmost_value_row, new_table.nrow):
                for j in range(new_table.ncol):
                    new_table[i, j].index_topleft_row -= \
                        (index_topmost_value_row - 1)

            # overwrite topmost row cell tokens
            for j in range(new_table.ncol):
                new_table[0, j].tokens = reduce(
                    lambda l1, l2: l1 + l2,
                    [c.tokens for c in new_table[:index_topmost_value_row, j]]
                )

            # delete collapsed cols (except for leftmost)
            new_grid = np.delete(new_table.grid,
                                 list(range(1, index_topmost_value_row)),
                                 axis=0)
            new_table = Table(grid=new_grid.tolist())

        return new_table

    @property
    def nrow(self) -> int:
        return self.normalized_table.nrow

    @property
    def ncol(self) -> int:
        return self.normalized_table.ncol

    @property
    def shape(self) -> Tuple[int, int]:
        return self.normalized_table.shape

    def __getitem__(self, index: Union[int, slice, Tuple]) -> \
            Union[Cell, List[Cell]]:
        return self.normalized_table[index]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return format_grid([[str(cell) for cell in row]
                            for row in self.normalized_table.grid])

    def insert_row(self, index: int, row: List[Cell]):
        assert len(row) == self.ncol
        new_grid = np.insert(arr=self.normalized_table.grid,
                             obj=index, values=row, axis=0)
        for i in range(index, self.normalized_table.nrow + 1):
            for j in range(self.normalized_table.ncol):
                new_grid[i, j].index_topleft_row += 1
        self.normalized_table = Table(grid=new_grid.tolist())

    def insert_column(self, index: int, column: List[Cell]):
        assert len(column) == self.nrow
        new_grid = np.insert(arr=self.normalized_table.grid,
                             obj=index, values=column, axis=1)
        for i in range(self.normalized_table.nrow):
            for j in range(index, self.normalized_table.ncol + 1):
                new_grid[i, j].index_topleft_col += 1
        self.normalized_table = Table(grid=new_grid.tolist())

    def delete_row(self, index: int):
        new_grid = np.delete(arr=self.normalized_table.grid, obj=index, axis=0)
        for i in range(index, self.normalized_table.nrow - 1):
            for j in range(self.normalized_table.ncol):
                new_grid[i, j].index_topleft_row -= 1
        self.normalized_table = Table(grid=new_grid.tolist())

    def delete_column(self, index: int):
        new_grid = np.delete(arr=self.normalized_table.grid, obj=index, axis=1)
        for i in range(self.normalized_table.nrow):
            for j in range(index, self.normalized_table.ncol - 1):
                new_grid[i, j].index_topleft_col -= 1
        self.normalized_table = Table(grid=new_grid.tolist())

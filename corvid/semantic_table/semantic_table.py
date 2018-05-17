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

from corvid.table.table import Table, Cell
from corvid.util.strings import format_grid, count_digits, \
    remove_non_alphanumeric, is_like_citation


class SemanticTable(object):
    VALID_LABELS = ['metric', 'method', 'dataset', 'value', 'other', 'empty']
    ROW_LABELS = ['method']
    COL_LABELS = ['metric', 'dataset']

    def __init__(self, raw_table: Table):
        self.raw_table = raw_table
        self.normalized_table = self.normalize_table(raw_table=self.raw_table)

    # TODO: for now, simply returns the Table as-is (with 1x1 cells)
    def normalize_table(self, raw_table: Table) -> Table:
        new_cells = []
        for raw_cell in raw_table.cells:
            for i, j in raw_cell.indices:
                new_cells.append(
                    Cell(tokens=raw_cell.tokens,
                         index_topleft_row=i,
                         index_topleft_col=j,
                         rowspan=1,
                         colspan=1)
                )
        return Table(cells=new_cells,
                     nrow=raw_table.nrow,
                     ncol=raw_table.ncol)

    # TODO
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
        index_leftmost_value_col = self.ncol - 1
        while index_leftmost_value_col >= 0:
            if all([table[i, index_leftmost_value_col].label != 'VALUE'
                    for i in range(self.nrow)]):
                break
            index_leftmost_value_col -= 1
        index_leftmost_value_col += 1

        index_topmost_value_row = self.nrow - 1
        while index_topmost_value_row >= 0:
            if all([table[index_topmost_value_row, j].label != 'VALUE'
                    for j in range(self.ncol)]):
                break
            index_topmost_value_row -= 1
        index_topmost_value_row += 1

        # re-label bottom-right quadrant
        for i in range(index_topmost_value_row, self.nrow):
            for j in range(index_leftmost_value_col, self.ncol):
                table[i, j].label = 'VALUE'

        # re-label top-right quadrant
        for i in range(index_topmost_value_row):
            for j in range(index_leftmost_value_col, self.ncol):
                table[i, j].label = 'LABEL'

        # re-label bottom-left quadrant
        for i in range(index_topmost_value_row, self.nrow):
            for j in range(index_leftmost_value_col):
                table[i, j].label = 'LABEL'

        return index_topmost_value_row, index_leftmost_value_col

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

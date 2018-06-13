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
from copy import deepcopy

from corvid.table.table import Table, Cell
from corvid.util.strings import format_grid, count_digits, \
    remove_non_alphanumeric, is_like_citation


class NormalizationError(Exception):
    pass


class SemanticTable(object):
    def __init__(self, raw_table: Table):
        self.raw_table = raw_table
        self.normalized_table = self.normalize_table(table=self.raw_table)

    def normalize_table(self, table: Table) -> Table:
        raise NotImplementedError

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


class IdentitySemanticTable(SemanticTable):
    """Normalization that basically returns itself"""

    def normalize_table(self, table: Table) -> Table:
        new_cells = []
        for raw_cell in table.cells:
            for i, j in raw_cell.indices:
                new_cells.append(
                    Cell(tokens=raw_cell.tokens,
                         index_topleft_row=i,
                         index_topleft_col=j,
                         rowspan=1,
                         colspan=1))
        return Table(cells=new_cells, nrow=table.nrow, ncol=table.ncol)


class LabelCollapseSemanticTable(SemanticTable):
    """Normalization that collapses LABEL cells in rows and columns"""

    def normalize_table(self, table: Table) -> Table:

        # (1) classify every cell into `LABEL` or `VALUE`
        labels, index_topmost_value_row, index_leftmost_value_col = \
            self._classify_cells(table=table)

        if 'VALUE' not in labels:
            raise NormalizationError('No values in this table')

        # (2) split multispan cells into copies w/ span = 1
        new_table = self._standardize_cell_sizes(table=table)

        # (3) collapse label rows/cols to form single header & subject column
        new_table = self._merge_label_cells(
            table=new_table,
            index_topmost_value_row=index_topmost_value_row,
            index_leftmost_value_col=index_leftmost_value_col)

        # (4) if missing a header/subject (i.e. all `VALUE` cells), add empty one
        if index_topmost_value_row == 0:
            new_table = self._add_empty_header(table=new_table)

        if index_leftmost_value_col == 0:
            new_table = self._add_empty_subject(table=new_table)

        return new_table

    def _classify_cells(self, table: Table) -> Tuple[np.ndarray, int, int]:
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

        nrow, ncol = table.nrow, table.ncol

        labels = np.empty((nrow, ncol), dtype='<U10')

        # (1) first pass to do easy ones
        for cell in table.cells:

            text = remove_non_alphanumeric(str(cell))

            # RULE 0:  EMPTY CELLS ARE IGNORED
            if text == '':
                label = 'EMPTY'

            # RULE 1:  MULTIROW/COL CELLS ARE PROBABLY LABELS
            elif cell.rowspan > 1 or cell.colspan > 1:
                label = 'LABEL'

            # RULE 2:  A CELL WITH 100% TEXT IS PROBABLY A LABEL
            elif count_digits(text) == 0:
                label = 'LABEL'

            # RULE 3:  A CELL WITH >50% DIGITS IS PROBABLY A VALUE
            elif count_digits(text) / len(text) > 0.5:
                label = 'VALUE'

            else:
                label = 'UNKNOWN'

            for i, j in cell.indices:
                labels[i, j] = label

        # (2) second pass to form rectangle of 'VALUES'
        index_leftmost_value_col = ncol - 1
        while index_leftmost_value_col >= 0:
            if all(labels[:, index_leftmost_value_col] != 'VALUE'):
                break
            index_leftmost_value_col -= 1
        index_leftmost_value_col += 1

        index_topmost_value_row = nrow - 1
        while index_topmost_value_row >= 0:
            if all(labels[index_topmost_value_row, :] != 'VALUE'):
                break
            index_topmost_value_row -= 1
        index_topmost_value_row += 1

        # re-label top-left quadrant
        for i in range(index_topmost_value_row):
            for j in range(index_leftmost_value_col):
                labels[i, j] = 'EMPTY'

        # re-label top-right quadrant
        for i in range(index_topmost_value_row):
            for j in range(index_leftmost_value_col, table.ncol):
                labels[i, j] = 'LABEL'

        # re-label bottom-left quadrant
        for i in range(index_topmost_value_row, table.nrow):
            for j in range(index_leftmost_value_col):
                labels[i, j] = 'LABEL'

        # re-label bottom-right quadrant
        for i in range(index_topmost_value_row, table.nrow):
            for j in range(index_leftmost_value_col, table.ncol):
                labels[i, j] = 'VALUE'

        return labels, index_topmost_value_row, index_leftmost_value_col

    def _standardize_cell_sizes(self, table: Table) -> Table:
        """Creates new cells for multispan cells"""
        new_cells = []
        for raw_cell in table.cells:
            for i, j in raw_cell.indices:
                new_cell = Cell(tokens=raw_cell.tokens,
                                index_topleft_row=i,
                                index_topleft_col=j,
                                rowspan=1, colspan=1)
                new_cells.append(new_cell)
        return Table(cells=new_cells, nrow=table.nrow, ncol=table.ncol)

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

    def _add_empty_header(self, table: Table) -> Table:
        for cell in table.cells:
            cell.index_topleft_row += 1
        new_grid = np.insert(
            table.grid, 0, values=[Cell(tokens=[],
                                        index_topleft_row=0,
                                        index_topleft_col=j,
                                        rowspan=1, colspan=1)
                                   for j in range(table.ncol)],
            axis=0
        )
        new_table = Table(grid=new_grid)
        return new_table

    def _add_empty_subject(self, table: Table) -> Table:
        for cell in table.cells:
            cell.index_topleft_col += 1
        new_grid = np.insert(
            table.grid, 0, values=[Cell(tokens=[],
                                        index_topleft_row=i,
                                        index_topleft_col=0,
                                        rowspan=1, colspan=1)
                                   for i in range(table.nrow)],
            axis=1)
        new_table = Table(grid=new_grid)
        return new_table

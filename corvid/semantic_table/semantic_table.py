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
from corvid.util.strings import format_grid, count_digits


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
    def _classify_cells(self, cells: List[Cell]) -> List[str]:
        pred_cell_labels = []

        # (1) first pass to do easy ones
        for cell in cells:

            text = str(cell)

            # RULE 0:  EMPTY CELLS ARE IGNORED
            if str(cell) == '':
                pred_cell_labels.append('EMPTY')

            # RULE 1:  MULTIROW/COL CELLS ARE PROBABLY LABELS
            elif cell.rowspan > 1 or cell.colspan > 1:
                pred_cell_labels.append('LABEL')

            # RULE 2:  A CELL WITH >50% DIGITS IS PROBABLY A VALUE
            elif count_digits(text) / len(text) > 0.5:
                pred_cell_labels.append('VALUE')

            else:
                # pred_cell_labels.append('UNKNOWN')
                pred_cell_labels.append('LABEL')

        # (2) second pass to use neighborhood info

        return pred_cell_labels

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

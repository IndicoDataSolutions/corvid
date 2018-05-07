"""


"""

from typing import List, Dict, Tuple, Union

import numpy as np

from corvid.semantic_table.table import Table, Cell


class SemanticTable(object):
    VALID_LABELS = ['metric', 'method', 'dataset', 'value', 'other', 'empty']

    def __init__(self, raw_table: Table):
        self.table = raw_table
        self.labels = self._classify_cells()
        # TODO: implement
        self.normalized_table = self._normalize_table()

    # TODO: implement
    def _classify_cells(self) -> List[str]:
        pred = []
        for cell in self.table.cells:
            pred.append(np.random.choice(SemanticTable.VALID_LABELS, size=1))
        return pred

    def _normalize_table(self) -> Table:
        pass

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

    # def __eq__(self, other: 'Table') -> bool:
    #     """Only compares Tables on whether they contain the same str(Cells).
    #     Doesnt compare other fields like `caption`, etc."""
    #
    #     assert self.nrow == other.nrow and self.ncol == other.ncol
    #
    #     for i in range(self.nrow):
    #         for j in range(self.ncol):
    #             if str(self[i, j]) != str(other[i, j]):
    #                 return False
    #     return True

    # def insert_row(self, index: int, row: List[Cell]) -> Table:
    #     assert len(row) == self.ncol
    #     new_grid = np.insert(arr=self.normalized_table.grid,
    #                          obj=index, values=row, axis=0)
    #     return Table(grid=new_grid)
    #
    # def insert_column(self, index: int, column: List[Cell]) -> Table:
    #     assert len(column) == self.nrow
    #     new_grid = np.insert(arr=self.normalized_table.grid,
    #                          obj=index, values=column, axis=1)
    #     return Table(grid=new_grid)
    #
    # def delete_row(self, index: int) -> Table:
    #     new_grid = np.delete(arr=self.normalized_table.grid, obj=index, axis=0)
    #     return Table(grid=new_grid)
    #
    # def delete_column(self, index: int) -> Table:
    #     new_grid = np.delete(arr=self.normalized_table.grid, obj=index, axis=1)
    #     return Table(grid=new_grid)
    #
    # def append_left(self, other: Table) -> Table:
    #     assert other.nrow == self.nrow
    #     new_grid = np.append(other.grid, self.normalized_table.grid, axis=1)
    #     return Table(grid=new_grid)
    #
    # def append_right(self, other: Table) -> Table:
    #     assert other.nrow == self.nrow
    #     new_grid = np.append(self.normalized_table.grid, other.grid, axis=1)
    #     return Table(grid=new_grid)
    #
    # def append_top(self, other: Table) -> Table:
    #     assert other.ncol == self.ncol
    #     new_grid = np.append(other.grid, self.normalized_table.grid, axis=0)
    #     return Table(grid=new_grid)
    #
    # def append_bottom(self, other: Table) -> Table:
    #     assert other.ncol == self.ncol
    #     new_grid = np.append(self.normalized_table.grid, other.grid, axis=0)
    #     return Table.create_from_grid(new_grid)
    #
    # # TODO: decide what data (i.e. caption, box) to keep after transposing
    # # TODO: swap row-colspan for each cell
    # def transpose(self) -> 'Table':
    #     table = Table()
    #     table.grid = self.grid.transpose()
    #     return table

    # TODO: what happens to Box after collapsing?
    # def _collapse(self):
    #     """A Table is collapsible if:
    #
    #         - All cells in a row have the same rowspan > 1
    #         - All cells in a column have the same colspan > 1
    #
    #     e.g. the Table w/ the entire first row having rowspan 2 has grid:
    #             row1 | row1 | row1
    #             row1 | row1 | row1
    #             row2 | row2 | row2
    #
    #          can be collapsed to:
    #             row1 | row1 | row1
    #             row2 | row2 | row2
    #     """
    #     # collapse any collapsible rows
    #     for i in range(self.nrow):
    #         rowspan = self[i, 0].rowspan
    #         if rowspan > 1:
    #             j = 1
    #             while self[i, j].rowspan == rowspan and j < self.ncol:
    #                 j += 1
    #
    #             is_row_collapsible = j == self.ncol
    #             if is_row_collapsible:
    #                 for j in range(self.ncol):
    #                     self[i, j].rowspan = 1
    #
    #     # collapse any collapsible columns
    #     for j in range(self.ncol):
    #         colspan = self[0, j].colspan
    #         if colspan > 1:
    #             i = 1
    #             while self[i, j].colspan == colspan and i < self.nrow:
    #                 i += 1
    #
    #             is_col_collapsible = i == self.nrow
    #             if is_col_collapsible:
    #                 for i in range(self.nrow):
    #                     self[i, j].colspan = 1

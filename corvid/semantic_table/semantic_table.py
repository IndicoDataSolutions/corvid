"""


"""

from typing import List, Tuple, Union

import numpy as np

from corvid.table.table import Table, Cell


class SemanticTable(object):
    VALID_LABELS = ['metric', 'method', 'dataset', 'value', 'other', 'empty']

    def __init__(self, raw_table: Table):
        self.raw_table = raw_table
        self.normalized_table = self._normalize_table()

    # TODO
    def _classify_cells(self) -> List[str]:
        pred_cell_labels = []
        for cell in self.raw_table.cells:
            pred_cell_labels.append(
                np.random.choice(SemanticTable.VALID_LABELS, size=1))
        return pred_cell_labels

    # TODO: for now, simply returns the Table as-is (with 1x1 cells)
    def _normalize_table(self) -> Table:
        # cell_labels = self._classify_cells()
        new_grid = [[None for _ in range(self.raw_table.ncol)]
                    for _ in range(self.raw_table.nrow)]
        for raw_cell in self.raw_table.cells:
            for i, j in raw_cell.indices:
                new_grid[i][j] = Cell(tokens=raw_cell.tokens,
                                      index_topleft_row=i,
                                      index_topleft_col=j,
                                      rowspan=1,
                                      colspan=1)
        normalized_table = Table(grid=new_grid)
        return normalized_table

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

        # def append_left(self, other: Table):
        #     assert other.nrow == self.nrow
        #     new_grid = np.append(other.grid, self.normalized_table.grid, axis=1)
        #     self.normalized_table = Table(grid=new_grid.tolist())
        #
        # def append_right(self, other: Table):
        #     assert other.nrow == self.nrow
        #     new_grid = np.append(self.normalized_table.grid, other.grid, axis=1)
        #     self.normalized_table = Table(grid=new_grid.tolist())
        #
        # def append_top(self, other: Table):
        #     assert other.ncol == self.ncol
        #     new_grid = np.append(other.grid, self.normalized_table.grid, axis=0)
        #     return Table(grid=new_grid)
        #
        # def append_bottom(self, other: Table):
        #     assert other.ncol == self.ncol
        #     new_grid = np.append(self.normalized_table.grid, other.grid, axis=0)
        #     return Table(grid=new_grid)

        # # TODO: decide what data (i.e. caption, box) to keep after transposing
        # # TODO: swap row-colspan for each cell
        # def transpose(self) -> 'Table':
        #     table = Table()
        #     table.grid = self.grid.transpose()
        #     return table
        #
        # # TODO: what happens to Box after collapsing?
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

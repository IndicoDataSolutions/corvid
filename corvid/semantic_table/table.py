"""

The Table class is a physical representation of tables extracted from documents

"""

from typing import List, Dict, Tuple, Union, Iterable, Callable

import numpy as np
import json

from corvid.util.geom import Box
from corvid.util.strings import format_grid

EMPTY_CAPTION = ''


class TableCreateException(ValueError):
    pass


class TableIndexException(IndexError):
    pass


class Token(object):
    """A single unit of text and metadata about that text"""

    def __init__(self, text: str, font: str = None, bounding_box: Box = None):
        self.text = text
        self.font = font
        self.bounding_box = bounding_box

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text


class Cell(object):
    """A Cell is a single unit of data in a Table separated from other Cells
    by whitespace and/or lines.  A Cell corresponds to its own row and
    column index (or indices) disjoint from those of other Cells."""

    def __init__(self, tokens: List[Token],
                 index_topleft_row: int, index_topleft_col: int,
                 rowspan: int = 1, colspan: int = 1,
                 bounding_box: Box = None):
        self.tokens = tokens
        self.index_topleft_row = index_topleft_row
        self.index_topleft_col = index_topleft_col
        self.rowspan = rowspan
        self.colspan = colspan
        self._bounding_box = bounding_box

    def __repr__(self):
        return ' '.join([str(token) for token in self.tokens])

    def __str__(self):
        return ' '.join([str(token) for token in self.tokens])

    @property
    def indices(self) -> List[Tuple[int, int]]:
        """Returns a list of indices for iterating over the Cell in
        top-to-bottom, left-to-right order.  For example, a 2x2 Cell starting
        at [1, 2] will return [(1, 2), (1, 3), (2, 2), (2, 3)]."""
        return [(self.index_topleft_row + i, self.index_topleft_col + j)
                for i in range(self.rowspan) for j in range(self.colspan)]

    @property
    def bounding_box(self) -> Box:
        """Finds bounding boxes that tightly bound all Tokens in the Cell"""
        if self._bounding_box:
            return self._bounding_box

        bounding_boxes = [token.bounding_box for token in self.tokens]

        if len(bounding_boxes) == 0 and not all(bounding_boxes):
            raise Exception('Tokens missing bounding boxes')

        return Box.compute_bounding_box(bounding_boxes)


# TODO: consider analogous method that returns all indices given a (multispan) cell
class Table(object):
    """A Table is a collection of Cells.  Visually, it may look like:

    >        |          header          |
    >        |  col1  |  col2  |  col3  |
    >  row1  |    a   |    b   |    c   |
    >  row2  |    d   |    e   |    f   |

    These Cells can be stored in two formats within a Table:

    (*) A grid-style format mimics a 2D matrix-like representation.
        It provides the concept of rows and columns, which
        induces a method of indexing using an [i,j] operator.

        Multirow/column Cells are treated in the grid-style format as having
        multiple indices that return the same Cell object.  For example:

    >  [0,0]       |  [0,1] header  |  [0,2] header  |  [0,3] header  |
    >  [1,0]       |  [1,1]  col1   |  [1,2]  col2   |  [1,3]  col3   |
    >  [2,0] row1  |  [2,1]   a     |  [2,2]   b     |  [2,3]   c     |
    >  [3,0] row2  |  [3,1]   d     |  [3,2]   e     |  [3,3]   f     |

       s.t. the same `header` Cell can be access via `[0,1]`, `[0,2]` or `[0,3]`


    (*) A list-style format handles multirow/column Cells by treating
        each Cell object (regardless of its size) as an individual item read
        from the Table in left-to-right, top-to-down fashion.

    >  [0]              > [5]  col3        > [10]  row2
    >  [1]  header      > [6]  row1        > [11]  d
    >  [2]              > [7]  a           > [12]  e
    >  [3]  col1        > [8]  b           > [13]  f
    >  [4]  col2        > [9]  c

       Here, each Cell is treated as a single element of the list, regardless
       of its row/colspan.

    NOTE:  We currently DON'T support list-style representation of Tables.
    """

    def __init__(self, paper_id: str = None,
                 page_num: int = None,
                 caption: str = EMPTY_CAPTION,
                 bounding_box: Box = None):

        self.grid = None
        self.cells = None
        self.paper_id = paper_id
        self.page_num = page_num
        self.caption = caption
        self._bounding_box = bounding_box

    @classmethod
    def create_from_grid(cls, grid: Iterable[Iterable[Cell]],
                         *args, **kwargs) -> 'Table':
        """Create a Table using 2D matrix/grid representation"""
        table = Table(*args, **kwargs)
        table.grid = np.array(grid)

        table.cells = []
        is_visited = [[False for _ in range(table.ncol)]
                      for _ in range(table.nrow)]
        for i in range(table.nrow):
            for j in range(table.ncol):
                if is_visited[i][j]:
                    continue
                else:
                    cell = table[i, j]
                    table.cells.append(cell)
                    for index_row, index_col in cell.indices:
                        is_visited[index_row][index_col] = True
        return table

    # TODO: creation of grid should be based on each cell's indices rather than assumed list order?
    @classmethod
    def create_from_cells(cls, cells: Iterable[Cell], nrow: int, ncol: int,
                          *args, **kwargs) -> 'Table':
        """Create a Table using list of Cells & desired 2D matrix dimensions"""
        table = Table(*args, **kwargs)
        table.cells = cells
        table.grid = np.array([[None for _ in range(ncol)]
                               for _ in range(nrow)])

        index_row, index_col = 0, 0
        for cell in cells:
            # insert copies of cell into grid based on its row/colspan
            for i in range(index_row, index_row + cell.rowspan):
                for j in range(index_col, index_col + cell.colspan):
                    table.grid[i, j] = cell

            # update `index_row` and `index_col` by scanning for next empty cell
            # jump index to next row if reach the right-most column
            while index_row < nrow and table.grid[index_row, index_col]:
                index_col += 1
                if index_col == ncol:
                    index_col = 0
                    index_row += 1

        # check that grid is complete (i.e. fully populated with cells)
        if not table.grid[-1, -1]:
            raise TableCreateException('Not enough cells to fill out table')

        return table

    @classmethod
    def create_from_json(cls, table_dict: Dict, tokenize: Callable,
                         *args, **kwargs) -> 'Table':
        """Create a Table using JSON dictionary"""

        spans = table_dict.get('spans')
        rows = table_dict.get('rows')

        # initialize grid of Cells
        if not isinstance(tokenize('test'), list):
            raise TableCreateException('`tokenize` should return List[str]')
        grid = [[Cell(tokens=[Token(text=s) for s in tokenize(text)],
                      index_topleft_row=i,
                      index_topleft_col=j)
                 for j, text in enumerate(row)] for i, row in enumerate(rows)]

        # overwrite any multispan Cells
        for span in spans:
            i_topleft_row, i_topleft_col = span.get('topleft')
            i_bottomright_row, i_bottomright_col = span.get('bottomright')
            cell = Cell(tokens=[Token(text=s) for s in tokenize(
                rows[i_topleft_row][i_topleft_col])],
                        index_topleft_row=i_topleft_row,
                        index_topleft_col=i_topleft_col,
                        rowspan=i_bottomright_row - i_topleft_row + 1,
                        colspan=i_bottomright_col - i_topleft_col + 1)
            for i, j in cell.indices:
                # verify specified cell span contains same text
                if rows[i][j] != rows[i_topleft_row][i_topleft_col]:
                    raise TableCreateException(
                        'Cell values differ within span [{},{}] x [{},{}]'
                            .format(i_topleft_row, i_topleft_col,
                                    i_bottomright_row, i_bottomright_col))
                grid[i][j] = cell

        table = Table.create_from_grid(grid=grid, *args, **kwargs)
        return table

    # def to_json(self) -> Dict:
    #     """Serialize to JSON dictionary"""
    #
    #     rows = [[str(self[i, j]) for j in range(self.ncol)]
    #             for i in range(self.nrow)]
    #
    #     # TODO: find way to iterate over each cell to skip doing stuff multiple times on multispan
    #     spans = []
    #     for i in range(self.nrow):
    #         for j in range(self.ncol):
    #             cell = self[i, j]
    #             if cell.rowspan > 1 or cell.colspan > 1:
    #                 spans.append({
    #                     'topleft': [
    #                         cell.index_topleft_row,
    #                         cell.index_topleft_col
    #                     ],
    #                     'bottomright': [
    #                         cell.index_topleft_row + cell.rowspan - 1,
    #                         cell.index_topleft_col + cell.colspan - 1
    #                     ],
    #                 })
    #
    #     return {'rows': rows, 'spans': spans}

    @property
    def nrow(self) -> int:
        return self.grid.shape[0]

    @property
    def ncol(self) -> int:
        return self.grid.shape[1]

    @property
    def shape(self) -> Tuple[int, int]:
        return self.grid.shape

    def __getitem__(self, index: Union[int, slice, Tuple]) -> \
            Union[Cell, List[Cell]]:
        """Indexes Table elements via its grid:
            * [int, int] returns a single Cell
            * [slice, int] or [int, slice] returns a List[Cell]
        or via its cells:
            * [int] returns a single Cell
            * [slice] returns a List[Cell]
        """
        if isinstance(index, tuple):
            grid = self.grid[index]
            if isinstance(grid, Cell):
                return grid
            elif len(grid.shape) == 1:
                return grid.tolist()
            else:
                raise TableIndexException('Not supporting [slice, slice]')
        elif isinstance(index, int) or isinstance(index, slice):
            return self.cells[index]
        else:
            raise TableIndexException('Only integers and slices')

    def __repr__(self):
        return format_grid([[str(cell) for cell in row]
                            for row in self.grid]) + '\n' + self.caption

    def __str__(self):
        return format_grid([[str(cell) for cell in row]
                            for row in self.grid]) + '\n' + self.caption

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

    # # TODO: unclear how to handle any *args **kwargs in either Table
    # def insert_rows(self, index: int, rows: 'Table') -> 'Table':
    #     assert isinstance(index, int)
    #
    #     # np.insert() works even if row.ncol < self.ncol, so to prevent this,
    #     # force equality in number of columns
    #     assert rows.ncol == self.ncol
    #
    #     # verify no multirow Cells in `self` are split by this insertion
    #     if any([self[index, j].index_topleft_row != index
    #             for j in range(self.ncol)]):
    #         raise TableIndexException(
    #             'Inserting into row {} would split a multirow cell'
    #                 .format(index))
    #
    #     # update indices of newly inserted cells
    #     for cell in rows.cells:
    #         cell.index_topleft_row += index
    #
    #     # update indices of any cells shifted lower by insertion
    #     shifted_cells = set([self[i, j] for i in range(index, self.nrow)
    #                          for j in range(self.ncol)])
    #     for cell in shifted_cells:
    #         cell.index_topleft_row += 1
    #
    #     # create new Table with updated grid
    #     new_grid = np.insert(arr=self.grid, obj=index, values=rows.grid, axis=0)
    #     table = Table.create_from_grid(new_grid)
    #
    #     # keep around any arguments in current Table
    #     kwargs = {key:val for key, val in self.__dict__.items()
    #               if key not in ['grid', 'cells']}
    #     table.__dict__.update(kwargs)
    #     return table

    #
    # def insert_column(self, index: int, column: List[Cell]) -> 'Table':
    #     assert len(column) == self.nrow
    #     new_grid = np.insert(arr=self.grid, obj=index, values=column, axis=1)
    #     return Table.create_from_grid(new_grid)
    #
    # def delete_row(self, index: int) -> 'Table':
    #     new_grid = np.delete(arr=self.grid, obj=index, axis=0)
    #     return Table.create_from_grid(new_grid)
    #
    # def delete_column(self, index: int) -> 'Table':
    #     new_grid = np.delete(arr=self.grid, obj=index, axis=1)
    #     return Table.create_from_grid(new_grid)
    #
    # def append_left(self, other: 'Table') -> 'Table':
    #     assert other.nrow == self.nrow
    #     new_grid = np.append(other.grid, self.grid, axis=1)
    #     return Table.create_from_grid(new_grid)
    #
    # def append_right(self, other: 'Table') -> 'Table':
    #     assert other.nrow == self.nrow
    #     new_grid = np.append(self.grid, other.grid, axis=1)
    #     return Table.create_from_grid(new_grid)
    #
    # def append_top(self, other: 'Table') -> 'Table':
    #     assert other.ncol == self.ncol
    #     new_grid = np.append(other.grid, self.grid, axis=0)
    #     return Table.create_from_grid(new_grid)
    #
    # def append_bottom(self, other: 'Table') -> 'Table':
    #     assert other.ncol == self.ncol
    #     new_grid = np.append(self.grid, other.grid, axis=0)
    #     return Table.create_from_grid(new_grid)

    # TODO: decide what data (i.e. caption, box) to keep after transposing
    # TODO: swap row-colspan for each cell
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

    @property
    def bounding_box(self) -> Box:
        """Finds bounding boxes that tightly bound all Cells in the Table"""
        if self._bounding_box:
            return self._bounding_box

        bounding_boxes = [cell.bounding_box
                          for cell in set(self.grid.flatten())]

        if len(bounding_boxes) == 0 and not all(bounding_boxes):
            raise Exception('Cells missing bounding boxes')

        return Box.compute_bounding_box(bounding_boxes)

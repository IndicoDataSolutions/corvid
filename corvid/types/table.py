"""

The Table class is a physical representation of tables extracted from documents

"""

from typing import List, Tuple, Callable, Union

import numpy as np

from corvid.util.geom import Box
from corvid.util.strings import format_grid

EMPTY_CAPTION = ''


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
    by whitespace and/or lines.  Typically corresponding to its own row and
    column index (or indices) disjoint from those of other Cells."""

    def __init__(self, tokens: List[Token],
                 rowspan: int = 1, colspan: int = 1,
                 bounding_box: Box = None):
        self.tokens = tokens
        self.rowspan = rowspan
        self.colspan = colspan
        self.bounding_box = bounding_box

    def __repr__(self):
        return ' '.join([str(token) for token in self.tokens])

    def __str__(self):
        return ' '.join([str(token) for token in self.tokens])

    def compute_bounding_box(self) -> Box:
        """Finds bounding boxes that tightly bound all Tokens in the Cell"""
        bounding_boxes = [token.bounding_box for token in self.tokens]

        if len(bounding_boxes) == 0 and not all(bounding_boxes):
            raise Exception('Tokens missing bounding boxes')

        return Box.compute_bounding_box(bounding_boxes)

    @classmethod
    def create_simple_cells(cls, token_strings: List[str],
                            tokenizer: Callable) -> 'List[Cell]':
        """Quickly instantiate a List[Cell] given a List[str] and a
        `tokenizer`, which takes a string input and outputs a List[Token].
        Each Cell will have the default row/colspan.
        """
        return [
            Cell(tokens=tokenizer(token_string))
            for token_string in token_strings
        ]


class Table(object):
    """A Table is a matrix representation of a collection of Cells:

    >        |          header          |
    >        |  col1  |  col2  |  col3  |
    >  row1  |    a   |    b   |    c   |
    >  row2  |    d   |    e   |    f   |

    These collections of Cells are stored in two formats within a Table:

    (*) A grid-style format mimics the matrix-like representation when we look
        at tables visually.  It provides the concept of rows and columns, which
        induces a method of indexing using an [i,j] operator.

        Multirow/column Cells are treated in the grid-style format as having
        multiple indices that return the same Cell object.  For example:

    >  [0,0]       |  [0,1] header  |  [0,2] header  |  [0,3] header  |
    >  [1,0]       |  [1,1]  col1   |  [1,2]  col2   |  [1,3]  col3   |
    >  [2,0] row1  |  [2,1]   a     |  [2,2]   b     |  [2,3]   c     |
    >  [3,0] row2  |  [3,1]   d     |  [3,2]   e     |  [3,3]   f     |

        where the same `header` Cell can be indexed from different columns


    (*) A list-style format handles multirow/column Cells by treating
        each Cell object (regardless of its size) as an individual item read
        from the table in left-to-right, top-to-down fashion.

    >  [0]              > [5]  col3        > [10]  row2
    >  [1]  header      > [6]  row1        > [11]  d
    >  [2]              > [7]  a           > [12]  e
    >  [3]  col1        > [8]  b           > [13]  f
    >  [4]  col2        > [9]  c

    """

    def __init__(self, paper_id: str = None,
                 page_num: int = None,
                 caption: str = EMPTY_CAPTION,
                 bounding_box: Box = None):

        self.grid = None
        self.paper_id = paper_id
        self.page_num = page_num
        self.caption = caption
        self.bounding_box = bounding_box

    @classmethod
    def create_from_grid(cls, grid: List[List[Cell]],
                         *args, **kwargs) -> 'Table':
        """Create a Table using List-of-List representation of Cell matrix"""
        table = Table(*args, **kwargs)
        table.grid = np.array(grid)
        return table

    @classmethod
    def create_from_cells(cls, cells: List[Cell], nrow: int, ncol: int,
                          *args, **kwargs) -> 'Table':
        """Create a Table using List of Cells & desired matrix dimensions"""
        table = Table(*args, **kwargs)
        table.grid = np.array([[None for _ in range(ncol)]
                               for _ in range(nrow)])

        index_insert_row, index_insert_col = 0, 0
        for cell in cells:
            # insert copies of cell into grid based on its row/colspan
            for i in range(index_insert_row, index_insert_row + cell.rowspan):
                for j in range(index_insert_col,
                               index_insert_col + cell.colspan):
                    table.grid[i, j] = cell

            # update `index_insert_*` by scanning along row for an empty cell
            # jump to next row if reach the end
            while index_insert_row < nrow and table.grid[
                index_insert_row, index_insert_col]:
                index_insert_col += 1
                if index_insert_col == ncol:
                    index_insert_col = 0
                    index_insert_row += 1

        # check for completeness
        if not table.grid[-1, -1]:
            raise Exception('Not enough cells to fill out the table')

        return table

    @property
    def nrow(self) -> int:
        return self.grid.shape[0]

    @property
    def ncol(self) -> int:
        return self.grid.shape[1]

    @property
    def dim(self) -> Tuple[int, int]:
        return self.grid.shape

    def __getitem__(self, index: Tuple) -> Union[Cell, List[Cell], 'Table']:
        """Indexes in similar manner as a 2D `np.ndarray`:
            * [int, int] returns a single Cell
            * [slice, int] or [int, slice] returns a List[Cell]
            * [slice, slice] returns a Table
        """
        if isinstance(index, tuple):
            grid = self.grid[index]
            if isinstance(grid, Cell):
                return grid
            elif len(grid.shape) == 1:
                return grid.tolist()
            return Table.create_from_grid(grid)
        else:
            raise Exception('Currently not supporting List-style indexing')

    def __repr__(self):
        return format_grid([[str(cell) for cell in row]
                            for row in self.grid]) + '\n' + self.caption

    def __str__(self):
        return format_grid([[str(cell) for cell in row]
                            for row in self.grid]) + '\n' + self.caption

    def __eq__(self, other: 'Table') -> bool:
        return np.array_equal(self.grid, other.grid)

    def insert_row(self, index: int, row: List[Cell]) -> 'Table':
        assert len(row) == self.ncol
        new_grid = np.insert(self.grid, obj=index, values=row, axis=0)
        return Table.create_from_grid(new_grid)

    def insert_column(self, index: int, column: List[Cell]) -> 'Table':
        assert len(column) == self.nrow
        new_grid = np.insert(arr=self.grid, obj=index, values=column, axis=1)
        return Table.create_from_grid(new_grid)

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

    def compute_bounding_box(self) -> Box:
        """Finds bounding boxes that tightly bound all Cells in the Table"""
        bounding_boxes = [cell.bounding_box
                          for cell in set(self.grid.flatten())]

        if len(bounding_boxes) == 0 and not all(bounding_boxes):
            raise Exception('Cells missing bounding boxes')

        return Box.compute_bounding_box(bounding_boxes)

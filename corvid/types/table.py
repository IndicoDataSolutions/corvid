"""

The Table class is a physical representation of tables extracted from documents

"""

from collections import namedtuple
from typing import List, Tuple

Point = namedtuple('Point', ['x', 'y'])

from corvid.util.strings import format_list, format_grid


class Token(object):
    """A single unit of text and metadata about that text"""

    def __init__(self, text: str, font: str = None,
                 lower_left: Point = None, upper_right: Point = None):
        self.text = text
        self.font = font
        self.lower_left = lower_left
        self.upper_right: upper_right

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text


class Cell(object):
    """A Cell is a single unit of data in a Table separated from other Cells
    by whitespace and/or lines.  Typically corresponding to its own row and
    column index (or indices) disjoint from those of other Cells."""

    def __init__(self, tokens: List[Token], rowspan: int = 1, colspan: int = 1,
                 lower_left: Point = None, upper_right: Point = None):
        self.tokens = tokens
        self.rowspan = rowspan
        self.colspan = colspan
        self.lower_left = lower_left
        self.upper_right: upper_right

    def __repr__(self):
        return format_list([str(token) for token in self.tokens])

    def __str__(self):
        return format_list([str(token) for token in self.tokens])


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

    def __init__(self, cells: List[Cell], nrow: int, ncol: int,
                 paper_id: str = None,
                 page_num: int = None,
                 caption: str = None,
                 lower_left: Point = None, upper_right: Point = None,
                 is_row_wise: bool = True):
        self.cells = cells
        self.nrow = nrow
        self.ncol = ncol

        self.grid = [[None for _ in range(ncol)] for _ in range(nrow)]
        index_row, index_col = 0, 0
        for cell in cells:

            if is_row_wise:
                # populate grid
                for i in range(index_row, index_row + cell.rowspan):
                    for j in range(index_col, index_col + cell.colspan):
                        self.grid[i][j] = cell

                # keep scanning right until empty cell; jump row if necessary
                while index_row < nrow and self.grid[index_row][index_col]:
                    index_col += 1
                    if index_col == ncol:
                        index_col = 0
                        index_row += 1
            else:
                for j in range(index_col, index_col + cell.colspan):
                    for i in range(index_row, index_row + cell.rowspan):
                        self.grid[i][j] = cell

                while index_col < ncol and self.grid[index_row][index_col]:
                    index_row += 1
                    if index_row == nrow:
                        index_row = 0
                        index_col += 1

        # check for completeness
        if (is_row_wise and index_col > 0) or \
                (not is_row_wise and index_row > 0):
            raise Exception('Not enough cells to fill out the table')

        self.paper_id = paper_id
        self.page_num = page_num
        self.caption = caption
        self.lower_left = lower_left
        self.upper_right: upper_right

    @property
    def dim(self) -> Tuple[int, int]:
        return self.nrow, self.ncol

    def __getitem__(self, index):
        if isinstance(index, tuple):
            if isinstance(index[0], slice):
                return [row[index[1]] for row in self.grid[index[0]]]
            return self.grid[index[0]][index[1]]
        else:
            return self.cells[index]

    def __repr__(self):
        return format_grid([[str(cell) for cell in row]
                            for row in self.grid])

    def __str__(self):
        return format_grid([[str(cell) for cell in row]
                            for row in self.grid])

    def transpose(self) -> 'Table':
        new_cells = [
            Cell(tokens=cell.tokens,
                 rowspan=cell.colspan,
                 colspan=cell.rowspan) for cell in self.cells
        ]

        return Table(cells=new_cells, nrow=self.ncol, ncol=self.nrow,
                     paper_id=self.paper_id, page_num=self.page_num,
                     caption=self.caption, is_row_wise=False)

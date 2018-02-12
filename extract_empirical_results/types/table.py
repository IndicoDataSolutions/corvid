"""

The Table class is a physical representation of tables extracted from documents

"""

from collections import namedtuple
from typing import List, Tuple

Point = namedtuple('Point', ['x', 'y'])

from extract_empirical_results.util.strings import format_grid


class Box(object):
    """A Box is a single unit of data on a Grid.

    For a Table in which all Cells have rowspan/colspan of 1, the Table
    is exactly equal to its Grid and each Cell is comprised of a single Box.
    Thus, a multirow/column Cell would be comprised of multiple Boxes.
    """

    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text


class Grid(object):
    """A Grid is a matrix representation of Boxes.  Tables are a higher-order
    understanding layered on top of a Grid.

    For example, Grids are always proper matrices (equal number of columns
    per row).  Hence, it's unambiguous to index the ith row and jth column
    in a Grid using the [i,j] operator.  And it's straightforward to perform
    operations like transposes.

    In contrast, Tables are collections of Cells which can span multiple Boxes.
    So for Tables, these basic operations are unintuitive to use.
    """

    def __init__(self, grid: List[List[Box]]):
        is_full_rank_grid = all([len(row) == len(grid[0]) for row in grid])
        if not is_full_rank_grid:
            raise Exception('Grid has differing number of columns per row')
        self.grid = grid

    @property
    def nrow(self) -> int:
        return len(self.grid)

    @property
    def ncol(self) -> int:
        return len(self.grid[0])

    @property
    def dim(self) -> Tuple[int, int]:
        return self.nrow, self.ncol

    def __getitem__(self, index: Tuple):
        if isinstance(index[0], slice):
            return [row[index[1]] for row in self.grid[index[0]]]
        return self.grid[index[0]][index[1]]

    # TODO: think whether want to give user this much access
    # def __setitem__(self, index: Tuple[int, int], box: Box):
    #     self.grid[index[0]][index[1]] = box

    def __repr__(self):
        return format_grid([[box.text for box in row]
                            for row in self.grid])

    def __str__(self):
        return format_grid([[box.text for box in row]
                            for row in self.grid])

    # TODO: think about whether want this to keep references to same Boxes
    def transpose(self) -> 'Grid':
        new_grid = Grid(**self.__dict__)
        new_grid.grid = [list(new_row) for new_row in zip(*self.grid)]
        return new_grid

    def flatten(self, row_wise: bool = True) -> List[Box]:
        if row_wise:
            return [self[i, j] for i in range(self.nrow)
                    for j in range(self.ncol)]
        else:
            return [self[i, j] for j in range(self.ncol)
                    for i in range(self.nrow)]


class Cell(object):
    """A Cell is a collection of Boxes within the same Grid that all carry
    the same text data but have different Grid indices

    `idx_*_start` and `idx_*_end` are (inclusive, exclusive) indices for
    slicing the provided Grid

    Once the source Grid is sliced, the Boxes corresponding to this Cell are
    themselves stored as a (smaller) Grid.  The Cell still maintains reference
    to the original source Grid.
    """

    def __init__(self, source_grid: Grid,
                 idx_col_start: int, idx_col_end: int,
                 idx_row_start: int, idx_row_end: int):
        self.cell = Grid(
            source_grid[idx_row_start:idx_row_end, idx_col_start:idx_col_end]
        )
        is_same_text_boxes = all([box.text == self.cell[0, 0].text
                                  for box in self.cell.flatten()])
        if not is_same_text_boxes:
            raise Exception('Cell requires all member Boxes to have same text')

        self.source_grid = source_grid
        self.idx_col_start = idx_col_start
        self.idx_col_end = idx_col_end
        self.idx_row_start = idx_row_start
        self.idx_row_end = idx_row_end

    @property
    def colspan(self) -> int:
        return self.idx_col_end - self.idx_col_start

    @property
    def rowspan(self) -> int:
        return self.idx_row_end - self.idx_row_start

    @property
    def boxes(self) -> List[Box]:
        return self.cell.flatten()

    def __repr__(self):
        return self.boxes[0].text

    def __str__(self):
        return self.boxes[0].text

    def __getitem__(self, index: Tuple) -> Box:
        return self.cell[index[0], index[1]]


class Table(object):
    """A Table is a physical representation of data presented in tabular
    format.  This class provides metadata about the table, and methods to
    for a user to work with the data within the table

    The core inputs are a Grid and a list of Cells defined over the Boxes in
    that input Grid.

    Two forms of indexing are supported:
        Grid-level:
            Use [i,j] on Table as you would on a Grid, and it returns a Box
        Cell-level:
            Use [i] on Table as you would on a List, and it returns a Cell
    """

    def __init__(self, grid: Grid, cells: List[Cell],
                 table_id: int, paper_id: int,
                 page_num: int, caption: str,
                 lower_left: Point = None, upper_right: Point = None):
        self.grid = grid
        self.cells = cells
        self.caption = caption
        self.table_id = table_id
        self.paper_id = paper_id
        self.page_num = page_num
        self.lower_left = lower_left
        self.upper_right: upper_right

    def __repr__(self):
        return self.grid.__repr__()

    def __str__(self):
        return self.grid.__str__()

        # TODO: maybe better to require user specify `.grid` or `.cells` to be more explicit
        # def __getitem__(self, index):
        #     if isinstance(index, tuple):
        #         return self.grid[index[0], index[1]]
        #     elif isinstance(index, int):
        #         return self.cells[index]
        #     else:
        #         raise Exception('Index must be a tuple of ints or a single int')

        # def __setitem__(self, index, value):
        #     if isinstance(index, tuple):
        #         if not isinstance(value, Box):
        #             raise Exception('Setter via [i,j] indexing requires Box input')
        #         self.grid[index[0]][index[1]] = value
        #     elif isinstance(index, int):
        #         if not isinstance(value, Cell):
        #             raise Exception('Setter via [i,j] indexing requires Cell input')
        #         self.cells[index] = value
        #     else:
        #         raise Exception('Index must be a tuple of ints or a single int')

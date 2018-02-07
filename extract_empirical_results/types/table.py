"""

Classes used to represent basic units of data for data generation:

- Instances represent each Input/Output pairing:  (Papers, Queries) -> Results

where:

- Papers are representations of a paper, and contain Numbers and Tables
- Queries are collections of keywords
- Results are (Number, label) pairings

where:

- Numbers contain data to locate a specific number in the Paper's abstract
- Tables are a representation of tables in the the Paper's body

"""

from collections import namedtuple
from typing import List, Tuple

from bs4 import Tag

Point = namedtuple('Point', ['x', 'y'])

from extract_empirical_results.util.util import format_list, format_matrix


class Cell(object):
    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class TetmlCell(Cell):
    def __init__(self, text: str = '', colspan: int = 1):
        self.colspan = colspan
        super(TetmlCell, self).__init__(text)

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text

    @classmethod
    def from_bs4_tag(cls, cell_tag: Tag) -> 'TetmlCell':
        """Create `TetmlCell` from bs4.Tag object containing `word` Tags"""
        text = format_list([w.get_text(strip=True)
                            for w in cell_tag.find_all('word')])
        colspan = int(cell_tag.get('colspan')) if cell_tag.get('colspan') else 1
        cell = TetmlCell(text=text, colspan=colspan)
        # lower_left = Point(x=cell_tag.get('llx'),
        #                    y=cell_tag.get('lly'))
        # upper_right = Point(x=cell_tag.get('urx'),
        #                     y=cell_tag.get('ury'))
        cell._tag = cell_tag
        return cell


class Table(object):
    """Class to represent physical structure of tables"""

    def __init__(self, matrix: List[List[Cell]]):
        self.matrix_raw = matrix

    @property
    def nrow(self) -> int:
        raise NotImplementedError

    @property
    def ncol(self) -> int:
        raise NotImplementedError

    @property
    def dim(self) -> Tuple[int, int]:
        raise NotImplementedError

    def __getitem__(self, indices: Tuple[int, int]) -> Cell:
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __contains__(self, cell: Cell) -> bool:
        raise NotImplementedError


class TetmlTable(Table):
    def __init__(self, matrix: List[List[TetmlCell]],
                 paper_id: str, page_num: int, table_id: int,
                 caption: str):
        self.paper_id = paper_id
        self.page_num = page_num
        self.table_id = table_id
        self.caption = caption
        self.matrix_unwound = TetmlTable._unwind_multicolumn_cells(matrix)
        self.is_rectangular = all([len(row) == len(self.matrix_unwound[0])
                                   for row in self.matrix_unwound])
        if not self.is_rectangular:
            raise Exception('Matrix has differing number of columns per row')
        super(TetmlTable, self).__init__(matrix)

    @property
    def nrow(self) -> int:
        return len(self.matrix_unwound)

    @property
    def ncol(self) -> int:
        return len(self.matrix_unwound[0])

    @property
    def dim(self) -> Tuple[int, int]:
        return self.nrow, self.ncol

    def __getitem__(self, indices: Tuple[int, int]) -> Cell:
        return self.matrix_unwound[indices[0]][indices[1]]

    def __repr__(self):
        return format_matrix([[cell.text for cell in row]
                              for row in self.matrix_unwound])

    def __str__(self):
        return format_matrix([[cell.text for cell in row]
                              for row in self.matrix_unwound])

    def __contains__(self, cell: Cell) -> bool:
        """Is this cell an element of this matrix?"""
        for i in range(self.nrow):
            for j in range(self.ncol):
                if cell is self[i, j]:
                    return True
        return False

    # TODO: implement
    def transpose(self) -> 'TetmlTable':
        raise NotImplementedError

    @classmethod
    def _unwind_multicolumn_cells(cls,
                                  matrix: List[List[TetmlCell]]) -> List[
        List[TetmlCell]]:
        """For each cell that spans multiple columns, unwinds by duplicating
        reference to this Cell across that row
        """
        new_matrix = []
        for row in matrix:
            new_row = []
            for cell in row:
                new_row.extend([cell] * cell.colspan)
            new_matrix.append(new_row)
        return new_matrix

    # TODO: implement
    @classmethod
    def _unwind_multirow_cells(cls,
                               matrix: List[List[TetmlCell]]) -> List[
        List[TetmlCell]]:
        """For each cell that spans multiple rows, unwinds by duplicating
        reference to this Cell through that column
        """
        raise NotImplementedError

    @classmethod
    def from_bs4_tag(cls, table_tag: Tag) -> 'TetmlTable':
        """Create `TetmlTable` from bs4.Tag object containing `row` and `cell` Tags"""
        matrix = [
            [
                TetmlCell.from_bs4_tag(cell_tag=cell)
                for cell in row.find_all('cell')
            ]
            for row in table_tag.find_all('row')
        ]
        # TODO: populate fields by parsing TETML
        table = TetmlTable(matrix=matrix,
                           paper_id='',
                           page_num=0,
                           table_id=0,
                           caption='')
        # lower_left = Point(x=table_tag.get('llx'),
        #                    y=table_tag.get('lly'))
        # upper_right = Point(x=table_tag.get('urx'),
        #                     y=table_tag.get('ury'))
        table._tag = table_tag
        return table

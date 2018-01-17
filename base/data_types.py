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

import re
import warnings
from collections import namedtuple
from typing import List, Dict, Tuple

from bs4 import Tag, BeautifulSoup

Point = namedtuple('Point', ['x', 'y'])

from base.util import format_list, format_matrix


class Number(object):
    def __init__(self, as_str: str):
        self.as_str = as_str
        try:
            self.as_num = int(as_str)
        except:
            self.as_num = float(as_str)

        # TODO: example forms of number representation
        self.as_span = None
        self.as_coordinates = None

    def __repr__(self):
        return self.as_str

    def __str__(self):
        return self.as_str


class Cell(object):
    def __init__(self, text: str = '', colspan: int = 1, **kwargs):
        self.text = text
        self.colspan = colspan

        self.__dict__.update(kwargs)

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text

    @classmethod
    def from_bs4_tag(cls, cell_tag: Tag) -> 'Cell':
        """Create `Cell` from bs4.Tag object containing `word` Tags"""
        cell = Cell(text=format_list([w.get_text(strip=True)
                                      for w in cell_tag.find_all('word')]),
                    colspan=int(cell_tag.get('colspan')) if cell_tag.get(
                        'colspan') else 1,
                    lower_left=Point(x=cell_tag.get('llx'),
                                     y=cell_tag.get('lly')),
                    upper_right=Point(x=cell_tag.get('urx'),
                                      y=cell_tag.get('ury')),
                    tag=cell_tag)

        return cell


class Table(object):
    def __init__(self, matrix: List[List[Cell]], **kwargs):
        self.raw_matrix = matrix

        self.clean_matrix = Table._unwind_multicolumn_cells(matrix)
        is_rectangular = all([len(row) == len(self.clean_matrix[0])
                              for row in self.clean_matrix])
        if not is_rectangular:
            raise Exception('Matrix has differing number of columns per row')

        self.__dict__.update(kwargs)

    @property
    def nrow(self) -> int:
        return len(self.clean_matrix)

    @property
    def ncol(self) -> int:
        return len(self.clean_matrix[0])

    @property
    def shape(self) -> Tuple[int, int]:
        return self.nrow, self.ncol

    def __getitem__(self, indices: Tuple[int, int]) -> Cell:
        return self.clean_matrix[indices[0]][indices[1]]

    def __repr__(self):
        return format_matrix([[cell.text for cell in row]
                              for row in self.clean_matrix])

    def __str__(self):
        return format_matrix([[cell.text for cell in row]
                              for row in self.clean_matrix])

    def __contains__(self, cell: Cell) -> bool:
        """Is this cell an element of this matrix?"""
        for i in range(self.nrow):
            for j in range(self.ncol):
                if cell is self[i, j]:
                    return True
        return False

    @classmethod
    def from_bs4_tag(cls, table_tag: Tag) -> 'Table':
        """Create `Table` from bs4.Tag object containing `row` and `cell` Tags"""
        matrix = [
            [Cell.from_bs4_tag(cell_tag=cell) for cell in row.find_all('cell')]
            for row in table_tag.find_all('row')
        ]
        table = Table(matrix=matrix,
                      lower_left=Point(x=table_tag.get('llx'),
                                       y=table_tag.get('lly')),
                      upper_right=Point(x=table_tag.get('urx'),
                                        y=table_tag.get('ury')),
                      tag=table_tag)
        return table

    @classmethod
    def _unwind_multicolumn_cells(cls,
                                  matrix: List[List[Cell]]) -> List[List[Cell]]:
        new_matrix = []
        for row in matrix:
            new_row = []
            for cell in row:
                new_row.extend([cell] * cell.colspan)
            new_matrix.append(new_row)
        return new_matrix


# TODO: this regex catches strings like "10,000,000" as 3 separate matches
class Paper(object):
    """

    The constructor takes inputs:
        `json`:  JSON representation of that paper
         `xml`:  TETML parse of that paper's PDF

    """

    def __init__(self, json: Dict, xml: BeautifulSoup):
        self._json = json
        self._xml = xml
        self.numbers = self._find_numbers()
        self.tables = self._find_tables()
        # TODO: merge tables
        # self.number_to_table = self._match_numbers_to_tables()

    @property
    def id(self):
        return self._json.get('id')

    @property
    def abstract(self):
        return self._json.get('paperAbstract')

    @property
    def venue(self):
        return self._json.get('venue')

    def _find_numbers(self) -> List[Number]:
        numbers = re.findall(pattern=r'[-+]?\d*\.\d+|\d+',
                             string=self.abstract)
        numbers = [Number(as_str=m) for m in numbers]

        is_duplicates = len(numbers) != len(set([n.as_num for n in numbers]))
        if is_duplicates:
            warnings.warn('Duplicate mentions in paper_id {}'.format(self.id))

        return numbers

    def _find_tables(self) -> List[Table]:
        tables = [Table.from_bs4_tag(table_tag=table)
                  for table in self._xml.find_all('table')]
        # TODO: remove unusable tables
        return tables

    # TODO: filter unusable tables in `_find_tables()`
    # @staticmethod
    # def _filter_tables(tables: List[Table]) -> List[Table]:
    #     valid_tables = []
    #     for table in tables:
    #         pass
    #     return tables

    # TODO: method to trace numbers in abstract to some table
    # def _match_numbers_to_tables(self) -> Dict[Number, Table]:
    #     matches = {}
    #     matches.update({self.numbers[0]: self.tables[0]})
    #     return matches


class Query(object):
    def __init__(self, keywords: List[str]):
        self.keywords = keywords

    # # TODO: unfinished; generates query from paper abstract
    # @classmethod
    # def from_paper(self, paper: Paper) -> List['Query']:
    #     keywords = ['a']
    #     queries = []
    #     return queries


class Result(object):
    POSSIBLE_LABELS = ['RESULT', 'NOT_RESULT', 'UNSURE']

    def __init__(self, number: Number, label: str = None):
        self.number = number
        self._label = label

    @property
    def value(self):
        return self.number.as_num

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label: str):
        if label not in Result.POSSIBLE_LABELS:
            raise Exception('{} is invalid label'.format(label))
        self._label = label


class Instance(object):
    def __init__(self, paper: Paper, query: Query,
                 results: List[Result] = None):
        self.paper = paper
        self.query = query
        if results is None:
            results = []
        self.results = results

    @property
    def json(self) -> Dict:
        return {
            'paper_id': self.paper.id,
            'query': self.query.keywords,
            'results': [
                [result.value, result.label] for result in self.results
            ]
        }

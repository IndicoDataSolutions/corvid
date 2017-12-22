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

from typing import List, Dict, Tuple

from bs4 import Tag, BeautifulSoup

import re
import warnings

from data_generator.data_generator.util import format_matrix


class Number(object):
    def __init__(self, as_str: str):
        self.as_str = as_str
        try:
            self.as_num = int(as_str)
        except:
            self.as_num = float(as_str)
        self.as_span = None
        self.as_coordinates = None

    def __repr__(self):
        return self.as_str


# TODO: page_num identification will be necessary for merging
class Table(object):
    def __init__(self, table: Tag):
        self._table = table
        self.lower_left_x = self._table.attrs.get('llx')
        self.lower_left_y = self._table.attrs.get('lly')
        self.upper_right_x = self._table.attrs.get('urx')
        self.upper_right_y = self._table.attrs.get('ury')
        self.matrix = [
            [cell.get_text(strip=True) for cell in row.find_all('cell')]
            for row in table.find_all('row')
        ]

    @property
    def dim(self) -> Tuple[int, int]:
        return len(self.matrix), max([len(row) for row in self.matrix])

    def __getitem__(self, indices: Tuple[int, int]) -> str:
        return self.matrix[indices[0]][indices[1]]

    def __str__(self):
        return format_matrix(self.matrix)


# TODO: this regex catches strings like "10,000,000" as 3 separate matches
class Paper(object):
    def __init__(self, json: Dict, xml: BeautifulSoup):
        self._json = json
        self._xml = xml
        self.numbers = self._find_numbers()
        self.tables = self._find_tables()

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
        return [Table(table) for table in self._xml.find_all('table')]


# TODO: keeping as another class in case want to augment queries w/ other data
class Query(object):
    def __init__(self, keywords: List[str]):
        self.keywords = keywords


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

# """
#
# Classes used to represent basic units of data for data generation:
#
# - Instances represent each Input/Output pairing:  (Papers, Queries) -> Results
#
# where:
#
# - Papers are representations of a paper, and contain Numbers and Tables
# - Queries are collections of keywords
# - Results are (Number, label) pairings
#
# where:
#
# - Numbers contain data to locate a specific number in the Paper's abstract
# - Tables are a representation of tables in the the Paper's body
#
# """
#
# from typing import List, Dict, Tuple
#
# from bs4 import Tag, BeautifulSoup
#
# import re
# import warnings
#
# from collections import namedtuple
#
# Point = namedtuple('Point', ['x', 'y'])
#
# from data_generator.data_generator.util import format_matrix, is_contains_alpha, \
#     is_floatable
#
#
# class Number(object):
#     def __init__(self, as_str: str):
#         self.as_str = as_str
#         try:
#             self.as_num = int(as_str)
#         except:
#             self.as_num = float(as_str)
#         self.as_span = None
#         self.as_coordinates = None
#
#     def __repr__(self):
#         return self.as_str
#
#     def __str__(self):
#         return self.as_str
#
#
# class Cell(object):
#     VALID_TYPES = ['LABEL', 'VALUE']
#
#     def __init__(self, text: str = '',
#                  type: str = None,
#                  colspan: int = 1,
#                  table: Table = None,
#                  index_row: int = None,
#                  index_col: int = None,
#                  **kwargs):
#         self.text = text
#         self._type = type
#         self.colspan = colspan
#
#         self.table = table
#         self.index_row = index_row
#         self.index_col = index_col
#         self.__dict__.update(kwargs)
#
#     def __repr__(self):
#         return self.text
#
#     def __str__(self):
#         return self.text
#
#     @property
#     def type(self):
#         return self._type
#
#     @type.setter
#     def type(self, type: str):
#         if type in Cell.VALID_TYPES:
#             self._type = type
#         else:
#             raise Exception('{} is invalid type. Try one of {}'
#                             .format(type, Cell.VALID_TYPES))
#
#     @property
#     def row_neighbors(self) -> List['Cell']:
#         return self.table[self.index_row, :]
#
#     @property
#     def col_neighbors(self) -> List['Cell']:
#         return self.table[:, self.index_col]
#
#     @classmethod
#     def from_bs4_tag(cls, cell_tag: Tag) -> 'Cell':
#         cell = Cell(lower_left=Point(x=cell_tag.get('llx'),
#                                      y=cell_tag.get('lly')),
#                     upper_right=Point(x=cell_tag.get('urx'),
#                                       y=cell_tag.get('ury')),
#                     tag=cell_tag)
#         if cell_tag.get('colspan'):
#             cell.colspan = int(cell_tag.get('colspan'))
#         cell.text = cell_tag.get_text(strip=True)
#
#         # TODO: loop & join by space unless punctuation?
#         # self.text = ''
#         # for word in cell.find_all('word'):
#         #     text = word.get_text(strip=True)
#         #     if text similar to punctuation:
#         #         self.text.append(text)
#         #     else:
#         #         self.text.append(' ' + text)
#
#         return cell
#
#
# # TODO: verify that all row lengths are equal == sum(colspans) s.t. None colspan = 1
# # TODO: page_num identification will be necessary for merging
# class Table(object):
#     def __init__(self, matrix: List[List[Cell]], **kwargs):
#         self.raw_matrix = matrix
#
#         clean_matrix = Table._unwind_multicolumn_cells(matrix)
#         is_rectangular = all([len(row) == len(matrix[0]) for row in matrix])
#         if not is_rectangular:
#             raise Exception('Invalid matrix: Differing num columns per row')
#         Table._classify_cells(clean_matrix)
#
#         self.clean_matrix = None
#         # 3. classify cells as labels or values
#         # 4. merge adjacent labels
#
#         self.__dict__.update(kwargs)
#
#     @property
#     def dim(self) -> Tuple[int, int]:
#         return len(self.clean_matrix), len(self.clean_matrix[0])
#
#     def __getitem__(self, indices: Tuple[int, int]) -> Cell:
#         return self.clean_matrix[indices[0]][indices[1]]
#
#     def __repr__(self):
#         return format_matrix([[cell.text for cell in row]
#                               for row in self.clean_matrix])
#
#     def __str__(self):
#         return format_matrix([[cell.text for cell in row]
#                               for row in self.clean_matrix])
#
#     def __contains__(self, cell: Cell) -> bool:
#         nrow, ncol = self.dim
#         for i in range(nrow):
#             for j in range(ncol):
#                 if cell is self[i, j]:
#                     return True
#         return False
#
#     @classmethod
#     def from_bs4_tag(cls, table_tag: Tag) -> 'Table':
#         matrix = [
#             [Cell.from_bs4_tag(cell_tag=cell) for cell in row.find_all('cell')]
#             for row in table_tag.find_all('row')
#         ]
#         table = Table(matrix=matrix,
#                       lower_left=Point(x=table_tag.get('llx'),
#                                        y=table_tag.get('lly')),
#                       upper_right=Point(x=table_tag.get('urx'),
#                                         y=table_tag.get('ury')),
#                       tag=table_tag)
#         return table
#
#     @classmethod
#     def _unwind_multicolumn_cells(cls,
#                                   matrix: List[List[Cell]]) -> List[List[Cell]]:
#         new_matrix = []
#         for row in matrix:
#             new_row = []
#             for cell in row:
#                 new_row.extend([cell] * cell.colspan)
#             new_matrix.append(new_row)
#         return new_matrix
#
#     @classmethod
#     def _classify_cells(cls, matrix: List[List[Cell]]):
#         """For each cell in table, determine its type using table context"""
#         for i, row in enumerate(matrix):
#             for j, cell in enumerate(row):
#                 cell.type = Table._predict_cell_type(matrix, i, j)
#
#     # TODO: improve inference for detecting labels vs values
#     @classmethod
#     def _predict_cell_type(cls, matrix: List[List[Cell]],
#                            index_row: int, index_col: int) -> str:
#         cell = matrix[index_row][index_col]
#
#         is_left_column = index_col == 0
#         is_top_row = index_row == 0
#         is_empty = len(cell.text) == 0
#         is_text = is_contains_alpha(cell.text)
#         is_any_row_neighbor_text = any([is_contains_alpha(c.text)
#                                         for c in cell.row_neighbors])
#         is_any_col_neighbor_text = any([is_contains_alpha(c.text)
#                                         for c in cell.col_neighbors])
#         is_number = is_floatable(cell.text)
#         # is_any_neighbor_number = is_floatable(
#         #     matrix[index_row + 1][index_col].text
#         # ) or is_floatable(matrix[index_row][index_col + 1].text)
#         #
#
#         if is_left_column or is_top_row:
#             if is_text:
#                 return 'LABEL'
#             elif is_empty and \
#                     (is_any_row_neighbor_text or is_any_col_neighbor_text):
#                 return 'LABEL'
#             else:
#                 return 'VALUE'
#
#         if
#
#         # if empty cell, based on position
#         if is_empty:
#             if is_left_column or is_top_row:
#                 if is_any_row_neighbor_text
#
#             # if left column or top row, highly likely is label
#
#
# # TODO: this regex catches strings like "10,000,000" as 3 separate matches
# class Paper(object):
#     def __init__(self, json: Dict, xml: BeautifulSoup):
#         self._json = json
#         self._xml = xml
#         self.numbers = self._find_numbers()
#         self.tables = self._find_tables()
#         # TODO: merge tables
#         self.number_to_table = self._match_numbers_to_tables()
#
#     @property
#     def id(self):
#         return self._json.get('id')
#
#     @property
#     def abstract(self):
#         return self._json.get('paperAbstract')
#
#     @property
#     def venue(self):
#         return self._json.get('venue')
#
#     def _find_numbers(self) -> List[Number]:
#         numbers = re.findall(pattern=r'[-+]?\d*\.\d+|\d+',
#                              string=self.abstract)
#         numbers = [Number(as_str=m) for m in numbers]
#
#         is_duplicates = len(numbers) != len(set([n.as_num for n in numbers]))
#         if is_duplicates:
#             warnings.warn('Duplicate mentions in paper_id {}'.format(self.id))
#
#         return numbers
#
#     def _find_tables(self) -> List[Table]:
#         tables = [Table(table) for table in self._xml.find_all('table')]
#         # TODO: remove unusable tables
#         return tables
#
#     @staticmethod
#     def _filter_tables(tables: List[Table]) -> List[Table]:
#         valid_tables = []
#         for table in tables:
#             pass
#         return tables
#
#     # TODO: incomplete; method to trace numbers in abstract to some table
#     def _match_numbers_to_tables(self) -> Dict[Number, Table]:
#         matches = {}
#         matches.update({self.numbers[0]: self.tables[0]})
#         return matches
#
#
# class Query(object):
#     def __init__(self, keywords: List[str]):
#         self.keywords = keywords
#
#     @classmethod
#     def from_paper(self, paper: Paper) -> List['Query']:
#         keywords = ['a']
#         queries = []
#         return queries
#
#
# class Result(object):
#     POSSIBLE_LABELS = ['RESULT', 'NOT_RESULT', 'UNSURE']
#
#     def __init__(self, number: Number, label: str = None):
#         self.number = number
#         self._label = label
#
#     @property
#     def value(self):
#         return self.number.as_num
#
#     @property
#     def label(self):
#         return self._label
#
#     @label.setter
#     def label(self, label: str):
#         if label not in Result.POSSIBLE_LABELS:
#             raise Exception('{} is invalid label'.format(label))
#         self._label = label
#
#
# class Instance(object):
#     def __init__(self, paper: Paper, query: Query,
#                  results: List[Result] = None):
#         self.paper = paper
#         self.query = query
#         if results is None:
#             results = []
#         self.results = results
#
#     @property
#     def json(self) -> Dict:
#         return {
#             'paper_id': self.paper.id,
#             'query': self.query.keywords,
#             'results': [
#                 [result.value, result.label] for result in self.results
#             ]
#         }

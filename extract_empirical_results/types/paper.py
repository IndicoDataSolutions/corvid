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
#
# import re
# import warnings
# from typing import List, Dict
#
# from bs4 import BeautifulSoup
# from extract_empirical_results.types.table import Table
#
#
# class Number(object):
#     def __init__(self, as_str: str):
#         self.as_str = as_str
#         try:
#             self.as_num = int(as_str)
#         except ValueError:
#             self.as_num = float(as_str)
#
#         # TODO: example forms of number representation
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
# # TODO: this regex catches strings like "10,000,000" as 3 separate matches
# class Paper(object):
#     """
#
#     The constructor takes inputs:
#         `json`:  JSON representation of that paper
#          `xml`:  TETML parse of that paper's PDF
#
#     """
#
#     def __init__(self, json: Dict, xml: BeautifulSoup):
#         self._json = json
#         self._xml = xml
#         self.numbers = self._find_numbers()
#         self.tables = self._find_tables()
#         # TODO: merge tables
#         # self.number_to_table = self._match_numbers_to_tables()
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
#         tables = [Table.from_bs4_tag(table_tag=table)
#                   for table in self._xml.find_all('table')]
#         # TODO: remove unusable tables
#         return tables
#
#         # TODO: filter unusable tables in `_find_tables()`
#         # @staticmethod
#         # def _filter_tables(tables: List[Table]) -> List[Table]:
#         #     valid_tables = []
#         #     for table in tables:
#         #         pass
#         #     return tables
#
#         # TODO: method to trace numbers in abstract to some table
#         # def _match_numbers_to_tables(self) -> Dict[Number, Table]:
#         #     matches = {}
#         #     matches.update({self.numbers[0]: self.tables[0]})
#         #     return matches
#
#
# class Query(object):
#     def __init__(self, keywords: List[str]):
#         self.keywords = keywords
#
#         # # TODO: unfinished; generates query from paper abstract
#         # @classmethod
#         # def from_paper(self, paper: Paper) -> List['Query']:
#         #     keywords = ['a']
#         #     queries = []
#         #     return queries
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

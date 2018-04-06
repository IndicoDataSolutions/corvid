"""

Classes that take local XML (output of PDFToXMLParser) and instantiate Tables.
Typical usage is within TableExtractor that utilizes external PDF parsing tools.

"""
import os

from typing import Tuple, List
from bs4 import Tag, BeautifulSoup

try:
    import cPickle as pickle
except ImportError:
    import pickle

from corvid.types.table import Token, Cell, Table, Box, EMPTY_CAPTION


class XMLToTablesParserException(Exception):
    pass


class TetmlXMLToTablesParserException(XMLToTablesParserException):
    pass


class OmnipageXMLToTablesParserException(XMLToTablesParserException):
    pass


class XMLToTablesParser(object):
    def __init__(self, target_dir: str):
        if not os.path.exists(target_dir):
            raise FileNotFoundError('Target directory {} doesnt exist'
                                    .format(target_dir))
        self.target_dir = target_dir

    def parse(self, paper_id: str, source_xml_path: str, *args, **kwargs) -> str:
        """Instantiates Tables from an XML for a given Paper.
        Returns the local path of the pickled output of the parsing.
        Raises exception unless user implements `_parse()`
        """
        target_pkl_path = self.get_target_path(paper_id)
        tables = self._parse(paper_id, source_xml_path, *args, **kwargs)
        with open(target_pkl_path, 'wb') as f:
            pickle.dump(tables, f)
        return target_pkl_path

    def _parse(self, paper_id: str, source_xml_path: str,
               *args, **kwargs) -> List[Table]:
        """User should implement this.
        Recommended to catch Exceptions and then raise custom Exceptions
        based on XMLToTablesParserException.
        """
        raise NotImplementedError

    def get_target_path(self, paper_id: str) -> str:
        """Each XML to Tables parser is responsible for constructing output
        filenames given the paper_id and self.target_dir.  This includes any
        special nesting directories (e.g. multiple files output given paper_id)
        """
        return '{}.pickle'.format(os.path.join(self.target_dir, paper_id))


class TetmlXMLToTablesParser(XMLToTablesParser):
    def _parse(self, paper_id: str, source_xml_path: str,
               caption_search_window: int = 3,
               *args, **kwargs) -> List[Table]:

        with open(source_xml_path, 'r') as f:
            tetml = BeautifulSoup(f)

        tables = []
        table_id = 0
        num_success, num_fail = 0, 0
        tags = tetml.find_all(['table', 'para'])
        for index_tag, tag in enumerate(tags):

            if tag.name == 'para':
                continue

            elif tag.name == 'table':
                before, after = self._find_caption_candidates(
                    index_table_tag=index_tag,
                    all_tags=tags,
                    search_window=caption_search_window)

                try:
                    table = self._create_table_from_tetml(
                        table_id=table_id,
                        table_tag=tag,
                        caption=self._select_caption(before, after),
                        paper_id=paper_id
                    )
                    tables.append(table)
                    print('Parsed Table {}.'.format(table_id))
                    num_success += 1
                except Exception as e:
                    print(e)
                    print('Failed to parse Table {}. Skipping...'
                          .format(table_id))
                    num_fail += 1

                table_id += 1

            else:
                raise TetmlXMLToTablesParserException(
                    'Should only be seeing `table` and `para` tags')

        print('Successfully parsed {} of {} detected tables'
              .format(num_success, num_success + num_fail))

        return tables

    def _find_caption_candidates(self,
                                 index_table_tag: int,
                                 all_tags: List[Tag],
                                 search_window: int) -> Tuple[List[Tag],
                                                              List[Tag]]:
        """Returns `before` and `after` caption candidates, ordered from
        closest to furthest proximity to the current table tag"""

        table_tag = all_tags[index_table_tag]

        # get candidates seen before `table_tag`
        index_candidate = index_table_tag - 1
        before = []
        while len(before) < search_window and index_candidate >= 0:

            candidate_tag = all_tags[index_candidate]

            is_para_tag = candidate_tag.name == 'para'
            is_same_parent = candidate_tag.parent == table_tag.parent
            if is_para_tag and is_same_parent:
                before.append(candidate_tag)

            index_candidate -= 1

        # get candidates seen after `table_tag`
        index_candidate = index_table_tag + 1
        after = []
        while len(after) < search_window and index_candidate < len(all_tags):

            candidate_tag = all_tags[index_candidate]

            is_para_tag = candidate_tag.name == 'para'
            is_same_parent = candidate_tag.parent == table_tag.parent
            if is_para_tag and is_same_parent:
                after.append(candidate_tag)

            index_candidate += 1

        return before, after

    def _select_caption(self, before: List[Tag], after: List[Tag]) -> str:
        """Returns closest caption to table given neighboring `para` tags
        within `before` and `after` (sorted in proximity-to-table-tag order)

        search heuristics:
        - prioritizes `after` Tags over `before` Tags
        - prioritizes Tags nearest to Table
        """

        for para_tag in after + before:
            para_text = ' '.join([text.get_text(strip=True)
                                  for text in para_tag.find_all('text')])

            # heuristic for determining whether `para_text` is a caption
            if para_text.lower().startswith('table'):
                return para_text

        return EMPTY_CAPTION

    def _create_table_from_tetml(self,
                                 table_id: int,
                                 table_tag: Tag,
                                 paper_id: str,
                                 caption: str) -> Table:
        cells = []
        ncol_per_row = []
        for i, row_tag in enumerate(table_tag.find_all('row')):

            ncol_per_row.append(0)
            for cell_tag in row_tag.find_all('cell'):

                # BUILD LIST OF TOKENS
                tokens = []
                for word_tag in cell_tag.find_all('word'):
                    word_box_tag = word_tag.find('box')
                    token = Token(text=word_box_tag.get_text(strip=True),
                                  # `find_all` gets font per character,
                                  # but use `find` because assume font
                                  # is constant within same word
                                  font=word_box_tag
                                  .find('glyph').get('font'),
                                  bounding_box=Box(
                                      llx=float(word_box_tag.get('llx')),
                                      lly=float(word_box_tag.get('lly')),
                                      urx=float(word_box_tag.get('urx')),
                                      ury=float(word_box_tag.get('ury'))))
                    tokens.append(token)

                # BUILD CELL FROM LIST OF TOKENS
                cell = Cell(
                    tokens=tokens,
                    rowspan=1,
                    colspan=int(cell_tag.get('colspan')) \
                        if cell_tag.get('colspan') else 1
                )
                cells.append(cell)
                ncol_per_row[i] += cell.colspan

        # TODO: add more filters here if necessary
        if not all([ncol == ncol_per_row[0] for ncol in ncol_per_row]):
            raise TetmlXMLToTablesParserException(
                'Table {} has unequal columns per row. Skipping...'.format(
                    table_id))

        # TODO: `page_num` and `paper_id` fields
        # BUILD TABLE FROM LIST OF CELLS
        table = Table.create_from_cells(
            cells=cells,
            nrow=len(ncol_per_row),
            ncol=ncol_per_row[0],
            paper_id=paper_id,
            page_num=0,
            caption=caption)
        return table


class OmnipageXMLToTablesParser(XMLToTablesParser):
    def _parse(self, paper_id: str, source_xml_path: str,
               caption_search_window: int = 3,
               *args, **kwargs) -> List[Table]:

        with open(source_xml_path, 'rb') as f:
            xml = BeautifulSoup(f)

        tables = []
        table_id = 0
        num_success, num_fail = 0, 0
        tags = xml.find_all(['tablezone', 'textzone'])
        for index_tag, tag in enumerate(tags):

            if tag.name == 'textzone':
                continue

            elif tag.name == 'tablezone':
                before, after = self._find_caption_candidates(
                    index_table_tag=index_tag,
                    all_tags=tags,
                    search_window=caption_search_window)

                try:
                    table = self._create_table_from_omnipage_xml(
                        table_tag=tag,
                        caption=self._select_caption(before, after),
                        paper_id=paper_id
                    )
                    tables.append(table)
                    print('Parsed Table {}.'.format(table_id))
                    num_success += 1
                except Exception as e:
                    print(e)
                    print('Failed to parse Table {}. Skipping...'
                          .format(table_id))
                    num_fail += 1

                table_id += 1

            else:
                raise OmnipageXMLToTablesParserException(
                    'Should only be seeing `tablezone` and `textzone` tags')

        print('Successfully parsed {} of {} detected tables'
              .format(num_success, num_success + num_fail))

        return tables

    def _find_caption_candidates(self,
                                 index_table_tag: int,
                                 all_tags: List[Tag],
                                 search_window: int) -> Tuple[List[Tag],
                                                              List[Tag]]:
        """Returns `before` and `after` caption candidates, ordered from
        closest to furthest proximity to the current table tag"""

        # get candidates seen before `table_tag`
        index_candidate = index_table_tag - 1
        before = []
        while len(before) < search_window and index_candidate >= 0:

            candidate_tag = all_tags[index_candidate]

            if candidate_tag.name == 'textzone':
                before.append(candidate_tag)

            index_candidate -= 1

        # get candidates seen after `table_tag`
        index_candidate = index_table_tag + 1
        after = []
        while len(after) < search_window and index_candidate < len(all_tags):

            candidate_tag = all_tags[index_candidate]

            if candidate_tag.name == 'textzone':
                after.append(candidate_tag)

            index_candidate += 1

        return before, after

    def _select_caption(self, before: List[Tag], after: List[Tag]) -> str:
        """Returns closest caption to table given neighboring `para` tags
        within `before` and `after` (sorted in proximity-to-table-tag order)

        search heuristics:
        - prioritizes `after` Tags over `before` Tags
        - prioritizes Tags nearest to Table
        """

        for text_tag in after + before:

            text = ' '.join([text.get_text(strip=True)
                             for text in text_tag.find_all('wd')])

            # heuristic for determining whether `text` is a caption
            if text.lower().startswith('table'):
                return text

        return EMPTY_CAPTION

    def _create_table_from_omnipage_xml(self,
                                        table_tag: Tag,
                                        caption: str,
                                        paper_id: str) -> Table:

        ncol = len(table_tag.find('gridtable').find_all('gridcol'))
        nrow = len(table_tag.find('gridtable').find_all('gridrow'))

        cells = []
        for cell_tag in table_tag.find_all('cellzone'):

            # BUILD LIST OF TOKENS
            tokens = []
            for word_tag in cell_tag.find_all('wd'):
                token = Token(text=word_tag.get_text(strip=True))
                tokens.append(token)

            # BUILD CELL FROM LIST OF TOKENS
            cell = Cell(
                tokens=tokens,
                rowspan=int(cell_tag.get('gridrowtill')) - int(
                    cell_tag.get('gridrowfrom')) + 1,
                colspan=int(cell_tag.get('gridcoltill')) - int(
                    cell_tag.get('gridcolfrom')) + 1
            )
            cells.append(cell)

        # BUILD TABLE FROM LIST OF CELLS
        table = Table.create_from_cells(
            cells=cells,
            nrow=nrow,
            ncol=ncol,
            paper_id=paper_id,
            page_num=0,
            caption=caption)

        return table

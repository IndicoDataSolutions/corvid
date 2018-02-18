"""



"""

from typing import List
from bs4 import BeautifulSoup

from corvid.types.table import Token, Cell, Table, Point


class TableExtractor(object):
    @classmethod
    def extract_tables(cls, xml_like) -> List[Table]:
        raise NotImplementedError


class PdflibTableExtractor(TableExtractor):
    @classmethod
    def extract_tables(cls, tetml: BeautifulSoup) -> List[Table]:

        tables = []
        num_success, num_failed = 0, 0
        for table_id, table_tag in enumerate(tetml.find_all('table')):
            cells = []
            ncols = []
            for i, row_tag in enumerate(table_tag.find_all('row')):
                ncols.append(0)
                for cell_tag in row_tag.find_all('cell'):

                    # BUILD LIST OF TOKENS
                    tokens = []
                    for word_tag in cell_tag.find_all('word'):
                        word_box_tag = word_tag.find('box')
                        token = Token(text=word_box_tag.get_text(strip=True),
                                      # `find_all` will get font per character
                                      # but assume font is same within a word
                                      font=word_box_tag
                                      .find('glyph').get('font'),
                                      lower_left=Point(
                                          x=word_box_tag.get('llx'),
                                          y=word_box_tag.get('lly')),
                                      upper_right=Point(
                                          x=word_box_tag.get('urx'),
                                          y=word_box_tag.get('ury')))
                        tokens.append(token)

                    # BUILD CELL FROM LIST OF TOKENS
                    cell = Cell(
                        tokens=tokens,
                        rowspan=1,
                        colspan=int(cell_tag.get('colspan')) \
                            if cell_tag.get('colspan') else 1
                        # TODO: derive xy-coordinates from Tokens
                        # lower_left=Point(x=cell_tag.get('llx'),
                        #                  y=cell_tag.get('lly')),
                        # upper_right=Point(x=cell_tag.get('urx'),
                        #                   y=cell_tag.get('ury'))
                    )
                    cells.append(cell)
                    ncols[i] += cell.colspan

            # TODO: add more filters here if necessary
            is_equal_ncol_per_row = all([ncol == ncols[0] for ncol in ncols])
            if not is_equal_ncol_per_row:
                print('Table {} has unequal columns per row. Skipping...'
                      .format(table_id))
                num_failed += 1

            # BUILD TABLE FROM LIST OF CELLS
            try:
                table = Table(cells=cells,
                              nrow=len(ncols),
                              ncol=ncols[0],
                              paper_id='PAPER_ID',
                              page_num=0,
                              caption='Hi this is a caption',
                              lower_left=Point(x=table_tag.get('llx'),
                                               y=table_tag.get('lly')),
                              upper_right=Point(x=table_tag.get('urx'),
                                                y=table_tag.get('ury')))
                tables.append(table)
                print('Parsed Table {}.'.format(table_id))
                num_success += 1
            except Exception as e:
                print(e)
                print('Failed to parse Table {}. Skipping...'.format(table_id))
                num_failed += 1

        print('Successfully parsed {}/{} tables'
              .format(num_success, num_success + num_failed))

        return tables

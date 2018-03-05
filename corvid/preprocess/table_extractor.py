"""



"""

from collections import deque
from typing import Set, List, Deque, Dict
from bs4 import Tag, BeautifulSoup

from corvid.types.table import Token, Cell, Table, EMPTY_CAPTION


def extract_tables_from_tetml(tetml: BeautifulSoup,
                              caption_search_window: int = 3) -> List[Table]:
    tables: List[Table] = []
    num_success, num_failed = 0, 0

    para_tags: List[Tag] = []
    table_dicts: Deque[Dict] = deque()
    visited_para_tags: Set[Tag] = set()

    tags = tetml.find_all(['table', 'para'])
    total_num_tags = len(tags)
    max_table_id = 0
    for index_tag, tag in enumerate(tags):

        # store each `table` tag in queue along with the `para` tags
        # observed before & after the table (i.e. caption candidates)
        # also, keep track of `para` tags nested within each `table` tag
        # to avoid mistreating them as captions later
        if tag.name == 'table':
            visited_para_tags.update(tag.find_all('para'))

            table_dicts.append({
                'table_id': max_table_id,
                'table_tag': tag,
                'before': para_tags[-caption_search_window:],
                'after': [],
            })
            max_table_id += 1

        # store each newly-visited `para` tag (i.e. caption candidate) in queue
        # and update data for previously-seen `table` tags
        # also, keep track of `para` tags nested within each `para` tag
        # to avoid adding them as caption candidate twice
        elif tag.name == 'para':
            if tag not in visited_para_tags:
                para_tags.append(tag)

                visited_para_tags.add(tag)
                visited_para_tags.update(tag.find_all('para'))

                for table_dict in table_dicts:
                    table_dict['after'].append(tag)
        else:
            raise Exception('Should only be seeing `table` and `para` tags')

        # if possible, build any Tables from `table` tags; otherwise, skip
        while len(table_dicts) > 0:

            is_seen_enough = len(table_dicts[0]['after']) == \
                             caption_search_window
            is_eof = index_tag == total_num_tags - 1
            if is_seen_enough or is_eof:
                table_dict = table_dicts.popleft()

                try:
                    table = _create_table_from_tetml(
                        table_id=table_dict['table_id'],
                        table_tag=table_dict['table_tag'],
                        caption=_select_caption_from_tetml(
                            before=table_dict['before'],
                            after=table_dict['after'])
                    )
                    tables.append(table)
                    print('Parsed Table {}.'.format(table_dict['table_id']))
                    num_success += 1
                except Exception as e:
                    print(e)
                    print('Failed to parse Table {}. Skipping...'
                          .format(table_dict['table_id']))
                    num_failed += 1
            else:
                break

    print('Successfully parsed {} of {} detected tables'
          .format(num_success, num_success + num_failed))

    return tables


def _select_caption_from_tetml(before: List[Tag], after: List[Tag]) -> str:
    """Returns closest caption to table given neighboring `para` tags
    within `before` and `after` (sorted in chron. order left-to-right)

    search heuristics:
    - prioritizes `after` Tags over `before` Tags
    - prioritizes Tags nearest to Table
    """

    for para_tag in after + before[::-1]:
        para_text = ' '.join([text.get_text(strip=True)
                              for text in para_tag.find_all('text')])

        # heuristic for determining whether `para_text` is a caption
        if para_text.lower().startswith('table'):
            return para_text

    return EMPTY_CAPTION


def _create_table_from_tetml(table_id: int, table_tag: Tag,
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
                              # but use `find` instead because assume font
                              # is constant within same word
                              font=word_box_tag
                              .find('glyph').get('font'))
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
        raise Exception('Table {} has unequal columns per row. Skipping...'
                        .format(table_id))

    # BUILD TABLE FROM LIST OF CELLS
    table = Table(cells=cells,
                  nrow=len(ncol_per_row),
                  ncol=ncol_per_row[0],
                  paper_id='PAPER_ID',
                  page_num=0,
                  caption=caption)
    return table


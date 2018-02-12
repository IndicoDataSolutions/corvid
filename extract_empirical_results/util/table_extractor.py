"""



"""


#
# @classmethod
# def from_tetml(cls, cell_tag: Tag) -> 'Cell':
#     """Create `Cell` from bs4.Tag object containing `word` Tags"""
#     text = format_list([w.get_text(strip=True)
#                         for w in cell_tag.find_all('word')])
#     colspan = int(cell_tag.get('colspan')) if cell_tag.get('colspan') else 1
#     cell = Cell(text=text, colspan=colspan)
#     cell.lower_left = Point(x=cell_tag.get('llx'),
#                             y=cell_tag.get('lly'))
#     cell.upper_right = Point(x=cell_tag.get('urx'),
#                              y=cell_tag.get('ury'))
#     cell._tag = cell_tag
#     return cell
#
#
# # TODO: pdflib doesnt seem to detect multirow cells
# def _unwind_multirow_cells(cls,
#                            matrix: List[List[Cell]]) -> List[List[Cell]]:
#     """For each cell that spans multiple rows, unwinds by duplicating
#     reference to this Cell through that column
#     """
#     raise NotImplementedError
#
#
# # TODO: may need to use xycoord info since colspans can be messed up in tables with multirow cells
# def _unwind_multicolumn_cells(cls,
#                               matrix: List[List[Cell]]) -> List[List[Cell]]:
#     """For each cell that spans multiple columns, unwinds by duplicating
#     reference to this Cell across that row
#     """
#     new_matrix = []
#     for row in matrix:
#         new_row = []
#         for cell in row:
#             new_row.extend([cell] * cell.colspan)
#         new_matrix.append(new_row)
#     return new_matrix
#
#
# def from_tetml(cls, table_tag: Tag) -> 'Table':
#     """Create `Table` from bs4.Tag object containing `row` and `cell` Tags"""
#     matrix = [
#         [
#             Cell.from_tetml(cell_tag=cell)
#             for cell in row.find_all('cell')
#         ]
#         for row in table_tag.find_all('row')
#     ]
#     # TODO: populate fields by parsing TETML
#     table = Table(matrix=matrix,
#                   paper_id='',
#                   page_num=0,
#                   table_id=0,
#                   caption='')
#     # lower_left = Point(x=table_tag.get('llx'),
#     #                    y=table_tag.get('lly'))
#     # upper_right = Point(x=table_tag.get('urx'),
#     #                     y=table_tag.get('ury'))
#     table._tag = table_tag
#     return table
#

# self.matrix_unwound = Table._unwind_multicolumn_cells(matrix)
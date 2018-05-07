"""

Handles building of Tables from inputs other than `grid` or `cells`.
This constructor logic is kept outside of `Table` because it's easier to
manage subclassing of Cell and Table classes.

"""

from typing import Callable, Dict
from corvid.semantic_table.table import Cell, Table


class CellBuilder(object):
    def __init__(self, cell_type: Callable[..., Cell]):
        self.cell_type = cell_type

    def from_json(self, json: Dict) -> Cell:
        cell = self.cell_type(tokens=json['tokens'],
                              index_topleft_row=json['index_topleft_row'],
                              index_topleft_col=json['index_topleft_col'],
                              rowspan=json['rowspan'],
                              colspan=json['colspan'])
        return cell


class TableBuilder(object):
    def __init__(self,
                 table_type: Callable[..., Table],
                 cell_builder: CellBuilder):
        self.table_type = table_type
        self.cell_builder = cell_builder

    def from_json(self, json: Dict) -> Table:
        cells = [self.cell_builder.from_json(d) for d in json['cells']]
        table = Table(cells=cells, nrow=json['nrow'], ncol=json['ncol'])
        return table

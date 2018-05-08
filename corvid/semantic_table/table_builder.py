"""

Handles building of Tables from inputs other than `grid` or `cells`.
Builder design chosen because easier to work with when start subclassing Cell
and Table as opposed to needing to override @classmethods

"""

from typing import Callable, Dict

from corvid.semantic_table.table import Cell, Table


class CellBuilder(object):
    def __init__(self, cell_type: Callable[..., Cell]):
        self.cell_type = cell_type

    def from_json(self, json: Dict) -> Cell:
        required_keys = ['tokens', 'index_topleft_row', 'index_topleft_col',
                         'rowspan', 'colspan']
        kwargs = {k: v for k, v in json.items() if k not in required_keys}
        cell = self.cell_type(tokens=json['tokens'],
                              index_topleft_row=json['index_topleft_row'],
                              index_topleft_col=json['index_topleft_col'],
                              rowspan=json['rowspan'],
                              colspan=json['colspan'],
                              **kwargs)
        return cell


class TableBuilder(object):
    def __init__(self,
                 table_type: Callable[..., Table],
                 cell_builder: CellBuilder):
        self.table_type = table_type
        self.cell_builder = cell_builder

    def from_json(self, json: Dict) -> Table:
        required_keys = ['cells', 'nrow', 'ncol']
        kwargs = {k: v for k, v in json.items() if k not in required_keys}
        cells = [self.cell_builder.from_json(d) for d in json['cells']]
        table = Table(cells=cells, nrow=json['nrow'], ncol=json['ncol'],
                      **kwargs)
        return table

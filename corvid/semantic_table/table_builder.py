"""

Handles building of Tables from inputs other than `grid` or `cells`.
Builder design chosen because easier to work with when start subclassing Cell
and Table as opposed to needing to override @classmethods

"""

from typing import Callable, Dict, List

from corvid.semantic_table.table import Cell, Table


class CellBuilderException(KeyError):
    pass


class TableBuilderException(KeyError):
    pass


class CellBuilder(object):
    def __init__(self,
                 cell_type: Callable[..., Cell],
                 required_keys: List[str] = None):
        self.cell_type = cell_type
        self.required_keys = required_keys if required_keys else []

    def from_json(self, json: Dict) -> Cell:
        for k in self.required_keys:
            if not json.get(k):
                raise CellBuilderException('Missing key {}'.format(k))
        cell = self.cell_type(**json)
        return cell


class TableBuilder(object):
    def __init__(self,
                 table_type: Callable[..., Table],
                 cell_builder: CellBuilder,
                 required_keys: List[str] = None):
        self.table_type = table_type
        self.cell_builder = cell_builder
        self.required_keys = required_keys if required_keys else []

    def from_json(self, json: Dict) -> Table:
        for k in self.required_keys:
            if not json.get(k):
                raise TableBuilderException('Missing key {}'.format(k))
        cells = [self.cell_builder.from_json(d) for d in json['cells']]
        kwargs = {k: v for k, v in json.items() if k not in 'cells'}
        table = self.table_type(cells=cells, **kwargs)
        return table

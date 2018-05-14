# corvid

Table semantics and aggregation!

## Installation

This project requires **Python 3.6**.  We recommend you set up a conda environment:
 
```
conda create -n corvid python=3.6
source activate corvid
```

The dependencies are listed in the `requirements.in` file:

```
pip install -r requirements.in
```

After installing, you can run all the unit tests:

```
pytest tests/
```


## Project structure

```
|-- corvid/
|   |-- table/
|   |   |-- table.py
|   |   |-- table_loader.py
|   |-- semantic_table/
|   |   |-- semantic_table.py
|   |   |-- evaluate.py
|   |-- table_aggregation/
|   |   |-- schema_matcher.py
|   |   |-- evaluate.py
|-- tests/
|-- requirements.in
```

A few important things:
- `table.py` contains the `Table` class, which is the data structure used to represent Tables.  It's fine to think of `Table` as a wrapper around a 2D `numpy` array, where each `[i,j]` element represents a cell in the Table. 
 
- `semantic_table.py` contains the `SemanticTable` class.  It takes a `Table` object as input and learns a normalization of it, which can be accessed via `.normalized_table`.   

- `schema_matcher.py` contains the `SchemaMatcher` class.  The `.aggregate_tables()` method takes a list of `Table` objects and finds alignments between columns.  For example, a column "p" in Table 1 could be aligned with another column "precision" in Table 2.  The `.map_tables()` method uses these alignments to build a single aggregate Table.    
 
- `evaluate.py` contains a function `evaluate()` which computes a suite of performance metrics on a given a Gold Table and Predicted Table pair.  The `semantic_table` and `table_aggregation` modules have their own respective evaluation methods.

## Usage / API

#### `table`
First, instantiate a `Table` object:
```python
from corvid.table.table import Cell, Table
cells = [
    Cell(tokens=['a'], index_topleft_row=0, index_topleft_col=0, rowspan=1, colspan=1),
    Cell(tokens=['b'], index_topleft_row=0, index_topleft_col=1, rowspan=1, colspan=1),
    Cell(tokens=['c'], index_topleft_row=1, index_topleft_col=0, rowspan=1, colspan=1),
    Cell(tokens=['d'], index_topleft_row=1, index_topleft_col=1, rowspan=1, colspan=1),
]
table = Table(cells=cells, nrow=2, ncol=2)
```

You can access certain elements by indexing like you would a 2D array:
```python
# visualize
print(table)

# shape
table.nrow; table.ncol; table.dim

# indexing via grid
first_row = table[0,:]
first_col = table[:,0]
bottom_right_element = table[-1, -1]

# indexing via cells
first_cell = table[0]
```

You can serialize this object to JSON:
```python
import json
with open('myfilename', 'w') as f:
    json.dump(table.to_json(), f)
```

You can load it back in from JSON using the `Loader` classes:
```python
from corvid.table.table_loader import CellLoader, TableLoader
cell_loader = CellLoader(cell_type=Cell)
table_loader = TableLoader(table_type=Table, cell_loader=cell_loader)

with open('myfilename', 'r') as f:
    table = table_loader.from_json(json.load(f))
```

You can extend all of these classes to contain augmented information:
```python
class ColorfulCell(Cell):
    def __init__(self, color: str, ...):
        super().__init__(...)
        self.color = color

class ColorfulTableWithCaption(Table):
    def __init__(self, caption: str, ...):
        super().__init__(...)
        self.caption = caption

cells = [ColorfulCell(color='red', ...), ColorfulCell(color='blue', ...), ...]
table = ColorfulTableWithCaption(cells=cells, nrow=2, ncol=2, caption='red and blue cells')
```

Serialization of these objects is similar, but requires specification of the correct `Cell` and `Table` types:
```python
with open('myfilename', 'w') as f:
    json.dump(table.to_json(), f)
    
cell_loader = CellLoader(cell_type=ColorfulCell)
table_loader = TableLoader(table_type=ColorfulTableWithCaption, cell_loader=cell_loader)

with open('myfilename', 'r') as f:
    table = table_loader.from_json(json.load(f))
```


#### `semantic_table`

Normalize an existing `Table` object by creating a `SemanticTable` object:
```python
from corvid.semantic_table.semantic_table import SemanticTable
semantic_table = SemanticTable(raw_table=table)

print(semantic_table.normalized_table)
```

#### `table_aggregation`

Aggregate `Table` objects using a `SchemaMatcher`:
```python
from corvid.table_aggregation.schema_matcher import ColNameSchemaMatcher
schema_matcher = ColNameSchemaMatcher()
```

First, construct a list of `Tables`.  For best results, use `normalized_tables` from `SemanticTable`, but everything works on `raw_tables` as well.
```python
normalized_source_tables = [SemanticTable(raw_table=t).normalized_table for t in tables]
```

Second, build a "Schema" by initializing a `Table` object, which only has a single row containing column header strings.  For example: 
```python
schema_cells = [Cell(tokens=['header1'], ...), Cell(tokens=['header2'], ...)]    
schema_table = Table(cells=schema_cells, nrow=1, ncol=2)
```

Third, build list of `PairwiseMappings` which indicate the column alignments between pairs of `Tables`.
```python
pairwise_mappings = schema_matcher.map_tables(
    tables=normalized_source_tables,
    target_schema=schema_table
)
```

Finally, use these `PairwiseMappings` to build a single `Table` object that has the columns specified by the "Schema" `Table`. 
```python
aggregate_table = schema_matcher.aggregate_tables(
    pairwise_mappings=pairwise_mappings,
    target_schema=schema_table
)
```

To evaluate this aggregation, use:
```python
from corvid.table_aggregation.evaluate import evaluate
evaluate(gold_table=gold_table, pred_table=aggregate_table)
```

## TODO

#### `semantic_table`
- cell-wise classification of `raw_table` `Cells`
- evaluation for semantic table

## Future
- latex source to table (for training/evaluation)
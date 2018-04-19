# corvid

Extract and aggregate tables of empirical results from computer science papers!

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

#### Other dependencies
If you're interested in using one of the predefined Table extractors from the `table_extraction` module, you'll also need to install a tool to parse PDFs to XML.  We currently support **[PDFLib's TET toolkit v5.1](https://www.pdflib.com/download/tet/)** and **[Nuance's OmniPage Capture SDK v20.2](https://www.nuance.com/print-capture-and-pdf-solutions/optical-character-recognition/omnipage/omnipage-for-developers.html)**.  For TET, you'll need the path to the `bin/tet` executable after installation.  For OmniPage, you'll need to run `make` to build `corvid.cpp` within the module `omnipage/` in this repo.  

## Project structure

```
|-- corvid/
|   |-- table_extraction/
|   |   |-- table_extractor.py
|   |   |-- evaluate.py
|   |-- table_aggregation/
|   |   |-- schema_matcher.py
|   |   |-- evaluate.py
|   |-- types/
|   |   |-- table.py
|-- tests/
|-- config.py
|-- requirements.in
```

A few important things:
- `table.py` contains the `Table` class, which is the data structure used to represent Tables.  It's fine to think of `Table` as a wrapper around a 2D `numpy` array, where each `[i,j]` element represents a cell in the Table.

- `table_extractor.py` contains the `TableExtractor` class.  The `.extract()` method extracts `Table` objects from a PDF input.
 
- `schema_matcher.py` contains the `SchemaMatcher` class.  The `.aggregate_tables()` method takes a list of `Table` objects and finds alignments between columns.  For example, a column "p" in Table 1 could be aligned with another column "precision" in Table 2.  The `.map_tables()` method uses these alignments to build a single aggregate Table.    
 
- `evaluate.py` contains a function `evaluate()` which computes a suite of performance metrics on a given a Gold Table and Predicted Table pair.  The `table_extraction` and `table_aggregation` modules have their own respective evaluation methods.

## Usage / API

The repo contains two modules:

#### `table_extraction`




#### `table_aggregation`

## Example

First, prepare `paper_ids.txt` that looks like:

```
0ad9e1f04af6a9727ea7a21d0e9e3cf062ca6d75
eda636e3abae829cf7ad8e0519fbaec3f29d1e82
...
```

We can download PDFs from S3 for the papers in this file: 

```bash
python scripts/fetch_papers_pdfs_from_s3.py 
    --mode pdf 
    --paper_ids /path/to/paper_ids.txt 
    --input_url s3://url-with-pdfs
    --output_dir data/pdf/
```

After we download the PDFs, we can parse them into the TETML format using PDFLib's TET:

```bash
python scripts/parse_pdfs_to_tetml.py
    --parser /path/to/pdflib-tet-binary
    --input_dir data/pdf/
    --output_dir data/tetml/    
``` 

*If the options in scripts `fetch_papers_*.py` and `parse_pdfs_*.py` are left out, the scripts will attempt to use default values from a configuration file.  See our example in `example_config.py`.*

Now that we've processed all these papers to TETML format, let's try extracting tables from one of them:

```python
from bs4 import BeautifulSoup
from corvid.table_extraction.table_extractor import TetmlTableExtractor

TETML_PATH = 'data/tetml/0ad9e1f04af6a9727ea7a21d0e9e3cf062ca6d75.tetml'
with open(TETML_PATH, 'r') as f_tetml:
    tetml = BeautifulSoup(f_tetml)
    tables = TetmlTableExtractor.extract_tables(tetml)
```

Let's try manipulating the first table in this list:

```python
table = tables[0]

# visualize
print(table)

# shape
table.nrow; table.ncol; table.dim

# indexing via grid
first_row = table[0,:]
first_col = table[:,0]

# indexing via cells
first_cell = table[0]
```

## TODO

- read `aliases` from madeleine's annotation and add to `datasets.json`
0. font information in cells
1. finish evaluation module for table extraction; write example script for API
2. table normalizing function
3. reorganize `data/` file structure 
4. handling `box` after table transformations (maybe store externally from class)
5. maybe store all metadata non-specific to table externally from class  
6. tests for file/tetml utils
7. `[[cell for cell in row] for row in x]` make possible on Table `x` using `__iter__`; make `.grid` private after this 
8. table filter in Aggregation step 

## Extraction TODOs
1. Excel to Gold annotation script + guidelines (think about how to map multcells); start w/ gold/target tables for each dataset

8. Script for inspecting Table pickles
9. Naming.  Alignment seems to denote bidirectionality vs Mapping has direction.


## Future
- latex source to table (for training/evaluation)
- parsing heuristics




## Miscellaneous

#### Installing PDFLib's TET toolkit on OSX

After downloading the `.dmg`, you'll need to mount the file:

```bash
sudo hdiutil attach TET-5.1-OSX-Perl-PHP-Python-Ruby.dmg
```

You can then find the TET binary at

```bash
ls /Volumes/TET-5.1-OSX-Perl-PHP-Python-Ruby/bin/tet
```


# corvid

Extract and aggregate tables of empirical results from computer science papers!

## Installation

This project requires **Python 3.6**.

The dependencies are listed in the `requirements.in` file.

You'll also need **[PDFLib's TET toolkit v5.1](https://www.pdflib.com/download/tet/)** for parsing PDFs.  You'll need to provide the path to the binary executable under `bin/tet` after downloading and extracting.

After installing, you can run all the **tests** via:

```
cd corvid
pytest tests/
```

## Usage

First, prepare `paper_ids.txt` that looks like:

```
0ad9e1f04af6a9727ea7a21d0e9e3cf062ca6d75
eda636e3abae829cf7ad8e0519fbaec3f29d1e82
...
```

We can download PDFs from S3 for the papers in this file: 

```bash
python scripts/fetch_papers.py 
    --mode pdf 
    --paper_ids /path/to/paper_ids.txt 
    --input_url s3://url-with-pdfs
    --out_path data/pdf/
```

After we download the PDFs, we can parse them into the TETML format using PDFLib's TET:

```bash
python scripts/parse_pdfs.py
    --parser /path/to/pdflib-tet-binary
    --input_dir data/pdf/
    --output_dir data/tetml/    
``` 

*If the options in scripts `fetch_papers.py` and `parse_pdfs.py` are left out, the scripts will attempt to use default values from a configuration file.  See our example in `example_config.py`.*

Now that we've processed all these papers to TETML format, let's try extracting tables from one of them:

```python
from bs4 import BeautifulSoup
from corvid.preprocess.table_extractor import PdflibTableExtractor

TETML_PATH = 'data/tetml/0ad9e1f04af6a9727ea7a21d0e9e3cf062ca6d75.tetml'
with open(TETML_PATH, 'r') as f_tetml:
    tetml = BeautifulSoup(f_tetml)
    tables = PdflibTableExtractor.extract_tables(tetml)
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

0. font information in cells
1. finish evaluation module for table extraction; write example script for API
2. table normalizing function
3. reorganize `data/` file structure 
4. handling `box` after table transformations (maybe store externally from class)
5. maybe store all metadata non-specific to table externally from class  
6. tests for file/tetml utils
7. `[[cell for cell in row] for row in x]` make possible on Table `x` 

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


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

0. Prepare `paper_ids.txt` that looks like:

```
123456
123457
123458
...
```

1. Download PDFs from S3

```bash
python scripts/fetch_papers.py 
    --mode pdf 
    --paper_ids /path/to/paper_ids.txt 
    --input_url s3://url-with-pdfs
    --out_path data/pdf/
```

2. Parse PDFs to TETML format using PDFLib's TET

```bash
python scripts/parse_pdfs.py
    --parser /path/to/pdflib-tet-binary
    --input_dir data/pdf/
    --output_dir data/tetml/    
``` 

For the scripts in Steps 1 and 2, if options are left out, this script will attempt to read defaults from a `config.py` file.

3. Extract tables from a TETML file for a single paper

```python
from bs4 import BeautifulSoup
from corvid.preprocess.table_extractor import PdflibTableExtractor

with open(TETML_PATH, 'r') as f_tetml:
    tetml = BeautifulSoup(f_tetml)
    tables = PdflibTableExtractor.extract_tables(tetml)
```

4. Manipulate tables

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

1. evaluation for table extraction
2. latex source to table
3. parsing heuristics
4. semantic table class
5. loading serialized tables



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


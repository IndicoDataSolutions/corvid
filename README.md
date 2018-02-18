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



## TODO

1. evaluation for table extraction
2. latex source to table
3. parsing heuristics
4. semantic table class
5. loading serialized tables
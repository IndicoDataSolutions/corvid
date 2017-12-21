
# data_generator

Generate training and testing data!


## Usage

#### 1. Required inputs

You should have a collection of papers
 
 - represented as JSON objects
 
```json
{
    "id": "12345",
    "paperAbstract": "In this paper, we show...",
    ...
}
```

 - TETML files generated from raw PDF files
 
```python
from data_generator.data_generator.parser import parse_pdfs

PDFLIB_TET_BINARY = '/path/to/tet'
PDF_DIR = '/path/to/pdfs'
TETML_DIR = '/path/to/tetmls' 
parse_pdfs(tet_path=PDFLIB_TET_BINARY, pdf_dir=PDF_DIR, out_dir=TETML_DIR) 
```

#### 2. Get `Numbers` for each `Paper`

```python
from data_generator.data_generator.data_types import Paper

list_of_json = [{}, {}, ..., {}]
list_of_papers = [Paper(json) for json in list_of_json]
```

Instantiation of `Paper` objects will automatically extract `Numbers` from the `Paper.abstract` and store them in `Paper.numbers`.

#### 3. Generate `Queries` for each `Paper` 

```python
from data_generator.data_generator.data_types import Query

#EVERY PAPER NEEDS TO HAVE A CORRESPONDING PATH TO PDF FILE
list_of_queries = [Query.from_paper(paper)]
```


## File formats

#### JSON representation of Instances

Each `Instance` object has a `.json` property that returns:

```json
{
  "paper_id": "12345",
  "query": ["MNIST", "classification accuracy", "svm"],
  "results": [
    [90, "RESULT"],
    [10000, "NOT_RESULT"],
    [0.333, "UNSURE"]
  ]
}
```

#### TSV format for CrowdFlower


## Notes: Data processing steps

5. Match numbers in abstract to table values and record field names
5. Match field names back to abstract
6. Generate positive query based on matches
7. Generate negative examples:
    - Query-independent negatives:
        - Any numbers in abstract that couldn't be matched to table value
    - Query-dependent negatives:
    

# TODO
- Filter out papers
    - Not in Venue
    - No tables
    - No pdf in S3
    - No number in abstract
    - 4 pages max
- TETML only works for 10 pages or under
- API design for usage
- rename `instance.py` to be more descriptive (e.g. 'common' 'datatypes')
- `Mentions` rename to `Candidates`
- Refactor `build_tetml_from_pdf` in `parser.py` to be safer
- Refactor `fetch_one_pdf_from_s3` in `fetcher.py` to use `common utils` from `scholar-research/base`
- `beautifulsoup` for XML parsing
- `CrowdFlower` directory as subdirectory in `python`
- Generate `query` given a `Paper` 
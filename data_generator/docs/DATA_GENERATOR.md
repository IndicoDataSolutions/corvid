
# data_generator

Generate training and testing data!


## Usage

#### 1. Required inputs

You should have a paper represented in JSON format:
 
```json
{
    "id": "12345",
    "paperAbstract": "In this paper, we show...",
    ...
}
```

and also have its raw PDF processed into a TETML file using:
 
```python
from data_generator.data_generator.parser import parse_one_pdf, parse_pdfs

# to process a single PDF
parse_one_pdf(tet_path='/path/to/bin/tet',
              pdf_path='/path/to/pdfs/12345.pdf',
              out_dir='/path/to/tetmls/')

# to process all PDFS in a directory
parse_pdfs(tet_path='/path/to/bin/tet',
           pdf_dir='/path/to/pdfs/', 
           out_dir='/path/to/tetmls/') 
```

#### 2. `Paper` objects contain `Numbers` and `Tables`

```python
from bs4 import BeautifulSoup
from data_generator.data_generator.data_types import Paper

with open('/path/to/tetmls/12345.tetml', 'r') as f:
    paper = Paper(json={'id': '12345', 'paperAbstract': '...'},
                  xml=BeautifulSoup(f))
```

`Numbers` are extracted from `Paper.abstract` and stored in `Paper.numbers`.
`Tables` are extracted from the TETML file and stored in `Paper.tables`.

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
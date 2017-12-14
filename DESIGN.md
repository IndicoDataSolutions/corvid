

## Data processing

1. Fetch papers from S3  by batch of `paper_id`'s
2. Filter out papers
    - Not in Venue
    - No tables
    - No pdf in S3
    - No number in abstract
    - 4 pages max
3. Extract tables using `pdflib`
4. Locate numbers within abstract
5. Match numbers in abstract to table values and record field names
5. Match field names back to abstract
6. Generate positive query based on matches
7. Generate negative examples:
    - Query-independent negatives:
        - Any numbers in abstract that couldn't be matched to table value
    - Query-dependent negatives:
        - Any 

#### Raw data

```
asdf;ljasdf
```

#### JSON representation

Single instance:
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

<!--
Single instance maps to multiple row(s):
```tsv
paper_id    query                          result      label
---------------------------------------------------------------------
"12345"     "MNIST, class accuracy, svm"   "90"        1
"12345"     "MNIST, class accuracy, svm"   "10,000"    0
"12345"     "MNIST, class accuracy, svm"   ".333"      0
```
-->

Each instance maps to a TSV row:
```tsv
paper_id  abstract            result1  result2   result3  result4  result5  keyword1          keyword2          keyword3  keyword4  keyword5  is_result1  is_result2  is_result3  is_result4  is_result5      
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"12345"   "In this paper..."  "90"     "10,000"  ".333"                     "MNIST"           "class accuracy"  "svm"                 1         null      null     null     null
```

## Necessary components

#### Data processing

- Fetch papers from S2 storage
- Filter papers

- On each JSON object:
    - fetch `abstract` string given `paper_id`
    - propose candidate `results` given `abstract` string
     
- Convert JSON file to TSV file
- Convert TSV file back to JSON file

## Usage

```python
class Query(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Result(object):
    def __init__(self, ):
        pass
        

class Instance(object):
    def __init__(self, paper_id: str, query: List[str]):
        self.paper_id = paper_id
        self.query = query
        self.results = 
    def to_json(self):
        pass
    def to_tsv(self):
        pass
    
```


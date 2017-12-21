## How to setup CrowdFlower task

These instructions setup a CrowdFlower task that presents annotator with an abstract containing highlighted numbers, and asks annotator to select the numbers that correspond to results.

The key difficulty is getting CrowdFlower to handle a variable number of numbers in each abstract (and therefore, a variable number of CrowdFlower judgments per task). 

1. Upload raw input file in similar format as `example-raw.tsv`
2. Select `Split Columns` on `keyword_list` column
3. Copy `data_generator/crowdflower/example-task.html` into `Instructions`
4. Copy `data_generator/crowdflower/example-task.cml` into `CML` settings
5. Copy `data_generator/crowdflower/example-task.css` into `CSS` settings
6. Copy `data_generator/crowdflower/example-task.js` into `Javascript` settings

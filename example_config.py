"""

Example configuration file containing paths to other tools or directories

Variables defined in this file are imported in the scripts found in `scripts/`

"""

import os

from corvid.util.files import canonicalize_path

ES_PROD_URL = 'http://my.prod.es.server.url:8080/'
ES_DEV_URL = 'http://my.dev.es.server.url:8080/'
S3_PDFS_URL = 's3://my-s3-bucket-url'
TET_BIN_PATH = canonicalize_path('/Volumes/TET-5.1-OSX-Perl-PHP-Python-Ruby/bin/tet')

DATA_DIR = canonicalize_path('data/')
DATASETS_JSON = os.path.join(DATA_DIR, 'datasets.json')
PAPER_IDS_TXT = os.path.join(DATA_DIR, 'paper_ids.txt')
PAPERS_JSON = os.path.join(DATA_DIR, 'papers.json')
PDF_DIR = os.path.join(DATA_DIR, 'pdf/')
TETML_DIR = os.path.join(DATA_DIR, 'tetml/')


"""

Functions that fetch remote files:

- Paper JSONs from ElasticSearch API
- Paper PDFs from S3

"""

import os
import subprocess
from typing import Dict, List

import requests
import json


def read_one_paper_from_es(es_url: str, paper_id: str) -> Dict[str, str]:
    paper = requests.get(os.path.join(es_url, 'paper',
                                      'paper', paper_id)).json()
    if paper.get('found'):
        return paper.get('_source')
    else:
        raise Exception('paper_id {} not found'.format(paper_id))


# TODO: Only supporting 100 papers at once, just to keep ES server happy
def fetch_papers_from_es(es_url: str, paper_ids: List[str], out_file: str):
    if len(paper_ids) > 100:
        raise Exception('Too many papers at once!')
    papers = []
    with open(out_file, 'w') as f:
        for paper_id in paper_ids:
            try:
                print('Fetching paper_id {}'.format(paper_id))
                papers.append(read_one_paper_from_es(es_url, paper_id))
            except Exception as e:
                print(e)
                print('Skipping paper_id {}'.format(paper_id))
        json.dump(papers, f)


# TODO: use boto3
def fetch_one_pdf_from_s3(s3_url: str, paper_id: str, out_dir: str,
                          is_overwrite: bool = False):
    s3_filename = '{}/{}.pdf'.format(paper_id[:4], paper_id[4:])
    out_filename = '{}.pdf'.format(os.path.join(out_dir, paper_id))

    if os.path.exists(out_filename) and not is_overwrite:
        raise Exception('{} already exists'.format(out_filename))

    subprocess.run('aws s3 cp {} {}'.format(os.path.join(s3_url,
                                                         s3_filename),
                                            out_filename),
                   shell=True, check=True)


def fetch_pdfs_from_s3(s3_url: str, paper_ids: List[str], out_dir: str,
                       is_overwrite: bool = False) -> List[str]:
    """Fetches list of pdfs from s3 and returns list of successful ones"""
    successful = []
    for paper_id in paper_ids:
        try:
            print('Fetching paper_id {}'.format(paper_id))
            fetch_one_pdf_from_s3(s3_url, paper_id, out_dir, is_overwrite)
            successful.append(paper_id)
        except Exception as e:
            print(e)
            print('Skipping paper_id {}'.format(paper_id))
    return successful


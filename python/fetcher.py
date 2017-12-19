"""



"""

from typing import Dict, List

import os
import requests

import sys

import subprocess

from python.instance import Paper


def fetch_one_paper_from_es(es_url: str, paper_id: str) -> Dict:
    paper = requests.get(os.path.join(es_url, 'paper',
                                      'paper', paper_id)).json()
    if paper.get('found'):
        return paper.get('_source')
    else:
        raise Exception('paper_id {} not found'.format(paper_id))


# TODO: Only supporting 100 papers at once, just to keep ES server happy
def fetch_papers_from_es(es_url: str, paper_ids: List[str]) -> List[Paper]:
    if len(paper_ids) > 100:
        raise Exception('Too many papers at once!')
    papers = []
    for paper_id in paper_ids:
        try:
            print('Fetching paper_id {}'.format(paper_id))
            papers.append(Paper(fetch_one_paper_from_es(es_url, paper_id)))
        except Exception:
            print('Skipping paper_id {}'.format(paper_id))

    return papers


def fetch_one_pdf_from_s3(s3_url: str, paper_id: str, out_dir: str):
    s3_filename = '{}/{}.pdf'.format(paper_id[:4], paper_id[4:])
    out_filename = '{}.pdf'.format(os.path.join(out_dir, paper_id))
    if os.path.exists(out_filename):
        print('{} already exists'.format(out_filename))
    else:
        try:
            subprocess.run('aws s3 cp {} {}'.format(os.path.join(s3_url,
                                                                 s3_filename),
                                                    out_filename),
                           shell=True, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)


def fetch_pdfs_from_s3(s3_url: str, paper_ids: List[str], out_dir: str):
    for paper_id in paper_ids:
        try:
            print('Fetching paper_id {}'.format(paper_id))
            fetch_one_pdf_from_s3(s3_url, paper_id, out_dir)
        except Exception:
            print('Skipping paper_id {}'.format(paper_id))

"""

Miscellaneous functions for working with files

"""

import os
import subprocess

from typing import Dict, List, Callable

import json
import requests


def canonicalize_path(path: str):
    """Converts a path string to its canonical form (easier for comparisons)"""
    return os.path.abspath(os.path.realpath(os.path.expanduser(path)))


def is_url_working(url: str) -> bool:
    return requests.get(url).status_code >= 400


def read_one_json_from_es(es_url: str, paper_id: str,
                          convert_paper_id_to_es_endpoint: Callable) -> \
        Dict[str, str]:
    paper = requests.get(convert_paper_id_to_es_endpoint(es_url,
                                                         paper_id)).json()
    if paper.get('found'):
        return paper.get('_source')
    else:
        raise Exception('paper_id {} not found'.format(paper_id))


# TODO: Only supporting 100 papers at once, just to keep ES server happy
def fetch_jsons_from_es(es_url: str, paper_ids: List[str], out_file: str,
                        convert_paper_id_to_es_endpoint: Callable,
                        is_overwrite: bool = False):
    if len(paper_ids) > 100:
        raise Exception('Too many papers at once!')

    if os.path.exists(out_file) and not is_overwrite:
        raise Exception('{} already exists'.format(out_file))

    papers = []
    for paper_id in paper_ids:
        try:
            print('Fetching paper_id {}'.format(paper_id))
            papers.append(read_one_json_from_es(es_url,
                                                paper_id,
                                                convert_paper_id_to_es_endpoint))
        except Exception as e:
            print(e)
            print('Skipping paper_id {}'.format(paper_id))

    with open(out_file, 'w') as f:
        json.dump(papers, f)


# TODO: use boto3
def fetch_one_pdf_from_s3(s3_url: str, paper_id: str, out_dir: str,
                          convert_paper_id_to_s3_filename: Callable,
                          is_overwrite: bool = False):
    s3_filename = convert_paper_id_to_s3_filename(paper_id)
    out_filename = '{}.pdf'.format(os.path.join(out_dir, paper_id))

    if os.path.exists(out_filename) and not is_overwrite:
        raise Exception('{} already exists'.format(out_filename))

    subprocess.run('aws s3 cp {} {}'.format(os.path.join(s3_url,
                                                         s3_filename),
                                            out_filename),
                   shell=True, check=True)


# TODO: dont like this function does 2 things; separate responsibility?
def fetch_pdfs_from_s3(s3_url: str, paper_ids: List[str], out_dir: str,
                       convert_paper_id_to_s3_filename: Callable,
                       is_overwrite: bool = False) -> Dict[str, str]:
    """Fetches pdfs from s3 and returns names of successful fetches"""
    fetch_statuses = {}
    for paper_id in paper_ids:
        try:
            print('Fetching paper_id {}'.format(paper_id))
            fetch_one_pdf_from_s3(s3_url,
                                  paper_id,
                                  out_dir,
                                  convert_paper_id_to_s3_filename,
                                  is_overwrite)
            fetch_statuses.update({paper_id: 'SUCCESS'})
        except Exception as e:
            print(e)
            print('Skipping paper_id {}'.format(paper_id))
            fetch_statuses.update({paper_id: 'FAIL'})
    return fetch_statuses

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


# TODO: make agnostic to specific ES API
def read_one_json_from_es(es_url: str, paper_id: str,
                          convert_paper_id_to_es_endpoint: Callable) -> \
        Dict[str, str]:
    paper = requests.get(convert_paper_id_to_es_endpoint(es_url,
                                                         paper_id)).json()
    if paper.get('found'):
        return paper.get('_source')
    else:
        raise Exception('paper_id {} not found'.format(paper_id))


# TODO: use boto3
def fetch_one_pdf_from_s3(s3_url: str, paper_id: str, out_dir: str,
                          convert_paper_id_to_s3_filename: Callable,
                          is_overwrite: bool = False) -> str:
    s3_filename = convert_paper_id_to_s3_filename(paper_id)
    pdf_path = '{}.pdf'.format(os.path.join(out_dir, paper_id))

    if os.path.exists(pdf_path) and not is_overwrite:
        raise Exception('{} already exists'.format(pdf_path))

    subprocess.run('aws s3 cp {} {}'.format(os.path.join(s3_url,
                                                         s3_filename),
                                            pdf_path),
                   shell=True, check=True)

    return pdf_path

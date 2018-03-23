"""

Miscellaneous functions for working with files

"""

import os
import subprocess

from typing import Dict, List, Callable

import json
import requests
import boto3
from botocore.exceptions import ClientError


def canonicalize_path(path: str):
    """Converts a path string to its canonical form (easier for comparisons)"""
    return os.path.abspath(os.path.realpath(os.path.expanduser(path)))

# TODO: delete after confirm unneeded; replaced with `pipeline/pdf_parser` and `pipeline/paper_fetcher`
#
# def is_url_working(url: str) -> bool:
#     return requests.get(url).status_code < 400
#
#
# def is_s3_bucket_exists(bucket: str) -> bool:
#     s3 = boto3.resource('s3')
#     return s3.Bucket(bucket) in s3.buckets.all()
#
#
#
# # TODO: error handling of different exceptions
# def read_one_json_from_es(es_url: str,
#                           paper_id: str,
#                           convert_paper_id_to_es_endpoint: Callable) -> Dict[str, str]:
#     es_endpoint = convert_paper_id_to_es_endpoint(es_url, paper_id)
#     paper = requests.get(es_endpoint).json()
#     if paper.get('found'):
#         return paper.get('_source')
#     else:
#         raise Exception('paper_id {} not found'.format(paper_id))
#
#
#
# def fetch_one_pdf_from_s3(s3_bucket: str,
#                           paper_id: str,
#                           out_dir: str,
#                           convert_paper_id_to_s3_filename: Callable,
#                           is_overwrite: bool = False) -> str:
#     s3_filename = convert_paper_id_to_s3_filename(paper_id)
#     pdf_path = '{}.pdf'.format(os.path.join(out_dir, paper_id))
#
#     if os.path.exists(pdf_path) and not is_overwrite:
#         raise Exception('{} already exists'.format(pdf_path))
#
#     s3 = boto3.resource('s3')
#     s3.Object(s3_bucket, s3_filename).download_file(pdf_path)
#
#     return pdf_path


"""

Functions that fetch remote files:

- Paper JSONs from ElasticSearch API
- Paper PDFs from S3

"""

import os
import subprocess
import argparse
from typing import Dict, List

import requests
import json

from config import convert_paper_id_to_s3_filename, PAPER_IDS_TXT, PAPERS_JSON, \
    PDF_DIR, S3_PDFS_URL, ES_PROD_URL, ES_DEV_URL


def read_one_json_from_es(es_url: str, paper_id: str) -> Dict[str, str]:
    paper = requests.get(os.path.join(es_url, 'paper',
                                      'paper', paper_id)).json()
    if paper.get('found'):
        return paper.get('_source')
    else:
        raise Exception('paper_id {} not found'.format(paper_id))


# TODO: Only supporting 100 papers at once, just to keep ES server happy
def fetch_jsons_from_es(es_url: str, paper_ids: List[str], out_file: str,
                        is_overwrite: bool = False):
    if len(paper_ids) > 100:
        raise Exception('Too many papers at once!')

    if os.path.exists(out_file) and not is_overwrite:
        raise Exception('{} already exists'.format(out_file))

    papers = []
    with open(out_file, 'w') as f:
        for paper_id in paper_ids:
            try:
                print('Fetching paper_id {}'.format(paper_id))
                papers.append(read_one_json_from_es(es_url, paper_id))
            except Exception as e:
                print(e)
                print('Skipping paper_id {}'.format(paper_id))
        json.dump(papers, f)


# TODO: use boto3
def fetch_one_pdf_from_s3(s3_url: str, paper_id: str, out_dir: str,
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
                       is_overwrite: bool = False) -> List[str]:
    """Fetches pdfs from s3 and returns names of successful fetches"""
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', required=True, type=str,
                        help='enter `json` or `pdf`')
    parser.add_argument('-p', '--paper_ids', type=str,
                        help='enter path to local file containing paper_ids')
    parser.add_argument('-i', '--input_url', type=str,
                        help='enter url containing remote files to fetch')
    parser.add_argument('-o', '--out_path', type=str,
                        help='enter path to local file/directory to save output file(s)')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    args = parser.parse_args()

    paper_ids_filename = args.paper_ids if args.paper_ids else PAPER_IDS_TXT
    with open(paper_ids_filename, 'r') as f:
        paper_ids = f.read().splitlines()

    if args.mode == 'json':
        fetch_jsons_from_es(es_url=args.input_url if args.input_url else ES_PROD_URL,
                            paper_ids=paper_ids,
                            out_file=args.out_path if args.out_path else PAPERS_JSON,
                            is_overwrite=args.overwrite)
    elif args.mode == 'pdf':
        fetch_pdfs_from_s3(s3_url=args.input_url if args.input_url else S3_PDFS_URL,
                           paper_ids=paper_ids,
                           out_dir=args.out_path if args.out_path else PDF_DIR,
                           is_overwrite=args.overwrite)
    else:
        raise Exception('Currently only supports `json` and `pdf` modes.')

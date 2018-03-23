"""

Classes that interface with external resources and download files locally

"""


import os

import requests
import json

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError

import boto3
from botocore.exceptions import ClientError


# TODO: remove later; require user to implement own fetchers
from config import convert_paper_id_to_s3_filename, convert_paper_id_to_es_id


class S3PDFPaperFetcherException(Exception):
    pass


class ElasticSearchJSONPaperFetcherException(Exception):
    pass


class PaperFetcher(object):
    def fetch(self, paper_id: str) -> str:
        raise NotImplementedError


class S3PDFPaperFetcher(PaperFetcher):

    def __init__(self, bucket: str, target_pdf_dir: str):
        self.s3 = boto3.resource('s3')

        if self.s3.Bucket(bucket) not in self.s3.buckets.all():
            raise S3PDFPaperFetcherException('Bucket {} doesnt exist'.format(bucket))
        self.bucket = bucket

        if not os.path.exists(target_pdf_dir):
            raise FileNotFoundError('Target directory {} doesnt exist'.format(target_pdf_dir))
        self.target_pdf_dir = target_pdf_dir

    # TODO: maybe keep `Bucket()` in `self` and call `download_file()` off it?
    def fetch(self, paper_id: str):

        target_path = os.path.join(self.target_pdf_dir, paper_id)

        try:
            s3_filename = convert_paper_id_to_s3_filename(paper_id)
            self.s3.Object(self.bucket, s3_filename).download_file(target_path)
        except ClientError as e:
            print(e)
            if e.response['Error']['Code'] == '404':
                raise S3PDFPaperFetcherException('Couldnt find paper {}'.format(paper_id))
            else:
                raise S3PDFPaperFetcherException


class ElasticSearchJSONPaperFetcher(PaperFetcher):

    def __init__(self, host_url: str, index: str, doc_type: str, target_json_dir: str):
        self.es = Elasticsearch(host_url)

        if requests.get(host_url).status_code >= 400:
            raise ElasticSearchJSONPaperFetcherException('URL {} doesnt exist'.format(host_url))
        self.base_url = host_url

        self.index = index
        self.doc_type = doc_type

        if not os.path.exists(target_json_dir):
            raise FileNotFoundError('Target directory {} doesnt exist'.format(target_json_dir))
        self.target_pdf_dir = target_json_dir


    def fetch(self, paper_id: str):

        target_path = os.path.join(self.target_pdf_dir, paper_id)

        try:
            es_id = convert_paper_id_to_es_id(paper_id)
            result = self.es.get(index=self.index,
                                 doc_type=self.doc_type,
                                 id=es_id).get('_source')
            with open(target_path, 'w') as f:
                json.dump(result, f)
        except TransportError as e:
            print(e)
            if e.status_code == '404':
                raise ElasticSearchJSONPaperFetcherException('Couldnt find paper {}'.format(paper_id))
            else:
                raise ElasticSearchJSONPaperFetcherException


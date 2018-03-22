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

class S3FetchException(Exception):
    pass


class ElasticSearchFetchException(Exception):
    pass


class Fetcher(object):
    def fetch(self):
        raise NotImplementedError


class S3Fetcher(Fetcher):

    def __init__(self, bucket: str, target_dir: str):
        self.s3 = boto3.resource('s3')

        if self.s3.Bucket(bucket) not in self.s3.buckets.all():
            raise S3FetchException('Bucket {} doesnt exist'.format(bucket))
        self.bucket = bucket

        if not os.path.exists(target_dir):
            raise FileNotFoundError('Target directory {} doesnt exist'.format(target_dir))
        self.target_dir = target_dir

    # TODO: maybe keep `Bucket()` in `self` and call `download_file()` off it?
    def fetch(self,
              s3_filename: str,
              new_filename: str,
              is_overwrite: bool = False):

        target_path = os.path.join(self.target_dir, new_filename)

        if os.path.exists(target_path) and not is_overwrite:
            raise S3FetchException('{} already exists'.format(target_path))

        try:
            self.s3.Object(self.bucket, s3_filename).download_file(target_path)
        except ClientError as e:
            print(e)
            if e.response['Error']['Code'] == '404':
                raise S3FetchException('File {} doesnt exist'.format(s3_filename))
            else:
                raise S3FetchException


class ElasticSearchFetcher(Fetcher):

    def __init__(self, host_url: str):
        self.es = Elasticsearch(host_url)

        if requests.get(host_url).status_code >= 400:
            raise ElasticSearchFetchException('URL {} doesnt exist'.format(host_url))
        self.base_url = host_url


    def fetch(self,
              index: str,
              doc_type: str,
              id: str,
              target_path: str,
              is_overwrite: bool = False):

        if os.path.exists(target_path) and not is_overwrite:
            raise ElasticSearchFetchException('{} already exists'.format(target_path))

        try:
            result = self.es.get(index, doc_type, id).get('_source')
            with open(target_path, 'w') as f:
                json.dump(result, f)
        except TransportError as e:
            print(e)
            if e.status_code == '404':
                raise ElasticSearchFetchException('{} not found'.format(id))
            else:
                raise ElasticSearchFetchException


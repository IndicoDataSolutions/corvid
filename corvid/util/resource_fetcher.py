"""

Classes that interfaces with external resources and download Paper files locally

"""

import os

import requests
import json

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError

import boto3
from botocore.exceptions import ClientError


# TODO: remove later; require user to implement own fetchers
# try:
#     from config import convert_paper_id_to_s3_filename, convert_paper_id_to_es_id
# except ImportError as e:
#     print(e)
#     raise ImportError


class FetcherException(Exception):
    pass

class S3PaperPDFFetcherException(FetcherException):
    pass

class ElasticSearchPaperJSONFetcherException(FetcherException):
    pass


class Fetcher(object):
    def __init__(self, target_dir: str):
        if not os.path.exists(target_dir):
            raise FileNotFoundError('Target directory {} doesnt exist'.format(target_dir))
        self.target_dir = target_dir

    def fetch(self, paper_id: str) -> str:
        """Primary method for fetching a Paper resource given its id.
        Returns the local path of the fetched file.

        Raises exception unless user implements `_fetch()`
        """
        target_path = self.get_target_path(paper_id)
        self._fetch(paper_id, target_path)
        return target_path

    def _fetch(self, paper_id: str, target_path: str):
        raise NotImplementedError

    def get_target_path(self, paper_id: str) -> str:
        raise NotImplementedError


# class S3PaperPDFFetcher(Fetcher):
#
#     def __init__(self, bucket: str, target_dir: str):
#         self.s3 = boto3.resource('s3')
#
#         if self.s3.Bucket(bucket) not in self.s3.buckets.all():
#             raise S3PaperPDFFetcherException('Bucket {} doesnt exist'.format(bucket))
#         self.bucket = bucket
#
#         super(S3PaperPDFFetcher, self).__init__(target_dir)
#
#
#     # TODO: maybe keep `Bucket()` in `self` and call `download_file()` off it?
#     def _fetch(self, paper_id: str, target_path: str):
#         try:
#             s3_filename = convert_paper_id_to_s3_filename(paper_id)
#             self.s3.Object(self.bucket, s3_filename).download_file(target_path)
#         except ClientError as e:
#             print(e)
#             if e.response['Error']['Code'] == '404':
#                 raise S3PaperPDFFetcherException('Couldnt find paper {}'.format(paper_id))
#             else:
#                 raise S3PaperPDFFetcherException
#
#     def get_target_path(self, paper_id: str) -> str:
#         return '{}.pdf'.format(os.path.join(self.target_dir, paper_id))
#
#
# class ElasticSearchPaperJSONFetcher(Fetcher):
#
#     def __init__(self, host_url: str, index: str, doc_type: str, target_dir: str):
#         self.es = Elasticsearch(host_url)
#
#         if requests.get(host_url).status_code >= 400:
#             raise ElasticSearchPaperJSONFetcherException('URL {} doesnt exist'.format(host_url))
#         self.base_url = host_url
#
#         self.index = index
#         self.doc_type = doc_type
#
#         super(ElasticSearchPaperJSONFetcher, self).__init__(target_dir)
#
#
#     def _fetch(self, paper_id: str, target_path: str):
#         try:
#             es_id = convert_paper_id_to_es_id(paper_id)
#             result = self.es.get(index=self.index,
#                                  doc_type=self.doc_type,
#                                  id=es_id).get('_source')
#             with open(target_path, 'w') as f:
#                 json.dump(result, f)
#         except TransportError as e:
#             print(e)
#             if e.status_code == '404':
#                 raise ElasticSearchPaperJSONFetcherException('Couldnt find paper {}'.format(paper_id))
#             else:
#                 raise ElasticSearchPaperJSONFetcherException
#
#     def get_target_path(self, paper_id: str) -> str:
#         return '{}.json'.format(os.path.join(self.target_dir, paper_id))

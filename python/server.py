"""


"""

from typing import Dict

import os
import requests


class Server(object):
    def __init__(self, url, port):
        self.url = url
        self.port = port
        self.endpoint = '{}:{}'.format(url, port)

    def get_paper_by_id(self, paper_id: str):
        raise NotImplementedError


class ElasticSearchServer(Server):
    def get_paper_by_id(self, paper_id: str) -> Dict:
        paper = requests.get(os.path.join(self.endpoint, 'paper',
                                          'paper', paper_id)).json()
        if paper.get('found'):
            return paper.get('_source')
        else:
            raise Exception('paper_id {} not found'.format(paper_id))

class S3Server(Server):
    pass

from typing import Dict

import os
import argparse
import requests


class Server(object):
    def __init__(self, url, port):
        self.url = url
        self.port = port
        self.endpoint = '{}:{}'.format(url, port)


class ElasticSearchServer(Server):
    def get_paper_by_id(self, paper_id: str) -> Dict:
        return requests.get(os.path.join(self.endpoint, 'paper',
                                         'paper', paper_id)).json()['_source']


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('paper_id', type=str)
    parser.add_argument('--url', type=str)
    parser.add_argument('--port', type=str)
    return parser.parse_args(args)

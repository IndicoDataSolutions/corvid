"""

Fetcher grabs a JSON paper from AWS and returns it as a Paper object

"""

from typing import Dict

import sys

from python.util import ElasticSearchServer, parse_arguments


class Paper(object):
    def __init__(self, paper: Dict):
        self.paper = paper
        self.__dict__.update(paper)

    @property
    def abstract(self):
        return self.paperAbstract

    @property
    def venue(self):
        return self.venue


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    es_server = ElasticSearchServer(url=args.url, port=args.port)
    paper = Paper(paper=es_server.get_paper_by_id(paper_id=args.paper_id))
    print(paper.abstract)

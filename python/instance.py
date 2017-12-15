"""



"""

from typing import List

from python.fetcher import Mention, Paper


# TODO: keeping as another class in case want to augment queries w/ other data
class Query(object):
    def __init__(self, keywords: List[str]):
        self.keywords = keywords


class Result(object):
    POSSIBLE_LABELS = ['RESULT', 'NOT_RESULT', 'UNSURE']

    def __init__(self, mention: Mention, label: str = None):
        self.mention = mention
        self._label = label

    @property
    def value(self):
        return self.mention.as_num

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label: str):
        if label not in Result.POSSIBLE_LABELS:
            raise Exception('{} is invalid label'.format(label))
        self._label = label


class Instance(object):
    def __init__(self, paper: Paper, query: Query, results: List[Result]=None):
        self.paper = paper
        self.query = query
        self.results = results

    def json(self):
        pass





"""



"""

from typing import List, Dict

import re
import warnings


class Mention(object):
    def __init__(self, as_str: str):
        self.as_str = as_str
        try:
            self.as_num = int(as_str)
        except:
            self.as_num = float(as_str)
        self.as_span = None

    def __repr__(self):
        return self.as_str


# TODO: this regex catches 10,000,000 as 3 separate matches
class Paper(object):
    def __init__(self, paper: Dict):
        self._paper = paper
        self.mentions = self.find_mentions()

    @property
    def id(self):
        return self._paper.get('id')

    @property
    def abstract(self):
        return self._paper.get('paperAbstract')

    @property
    def venue(self):
        return self._paper.get('venue')

    def find_mentions(self) -> List[Mention]:
        mentions = re.findall(pattern=r'[-+]?\d*\.\d+|\d+',
                              string=self.abstract)
        mentions = [Mention(as_str=m) for m in mentions]

        is_duplicates = len(mentions) != len(set([m.as_num for m in mentions]))
        if is_duplicates:
            warnings.warn('Duplicate mentions in paper_id {}'.format(self.id))

        return mentions


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
    def __init__(self, paper: Paper, query: Query,
                 results: List[Result] = None):
        self.paper = paper
        self.query = query
        if results is None:
            results = []
        self.results = results

    @property
    def json(self) -> Dict:
        return {
            'paper_id': self.paper.id,
            'query': self.query.keywords,
            'results': [[result.value, result.label] for result in self.results]
        }


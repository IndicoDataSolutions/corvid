"""

Classes that interfaces with external resources and download Paper files locally

"""

import os


class FetcherException(Exception):
    pass


class Fetcher(object):
    def __init__(self, target_dir: str):
        if not os.path.exists(target_dir):
            raise FileNotFoundError('Target directory {} doesnt exist'
                                    .format(target_dir))
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
        """User should implement this.  Recommended to catch Exceptions
        and instead raise custom Exceptions based on FetcherException."""
        raise NotImplementedError

    def get_target_path(self, paper_id: str) -> str:
        """Each fetcher is responsible for constructing output filenames
        given the paper_id and self.target_dir.  This includes any special
        nesting directories (e.g. multiple files fetched given paper_id)"""
        raise NotImplementedError

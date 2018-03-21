"""



"""


from typing import List, Dict

from corvid.types.table import Table

class Dataset(object):
    def __init__(self,
                 name: str,
                 paper_id: str,
                 aliases: List[str],
                 gold_tables: List[Table],
                 cited_by_paper_ids: List[str]):
        self.name = name
        self.paper_id = paper_id
        self.aliases = aliases
        self.gold_tables = gold_tables
        self.cited_by_paper_ids = cited_by_paper_ids


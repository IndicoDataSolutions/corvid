"""



"""


from typing import List, Dict

from corvid.types.table import Table

class Dataset(object):
    def __init__(self,
                 name: str,
                 paper_id: str,
                 aliases: List[str],
                 gold_tables: List[Table]):
        self.name = name
        self.paper_id = paper_id
        self.aliases = aliases
        self.gold_tables = gold_tables


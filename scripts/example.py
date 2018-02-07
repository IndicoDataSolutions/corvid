"""

Example that creates Tables from TETML files and adds to corresponding JSON paper

"""

import os
import json

from bs4 import BeautifulSoup

from config import LOCAL_JSON_FILE, LOCAL_TETML_DIR
from extract_empirical_results.types.table import TetmlTable

if __name__ == '__main__':
    with open(LOCAL_JSON_FILE, 'r') as f_json:
        paper_dicts = json.load(f_json)
        for paper_dict in paper_dicts:
            paper_id = paper_dict.get('paperAbstract')
            tetml_path = '{}.tetml'.format(
                os.path.join(LOCAL_TETML_DIR, paper_id)
            )
            try:
                with open(tetml_path, 'r') as f_tetml:
                    xml = BeautifulSoup(f_tetml)
                    tables = [
                        TetmlTable.from_bs4_tag(table_tag=table)
                        for table in xml.find_all('table')
                    ]
                    paper_dict.update({'tables': tables})
            except FileNotFoundError as e:
                print(e)
                print('{} missing TETML file. Skipping...'.format(paper_id))

"""

Example that creates Tables from TETML files and writes them to a text file

"""

import os

from bs4 import BeautifulSoup

from config import DATA_DIR, TETML_DIR
from corvid.preprocess.table_extractor import TetmlTableExtractor

OUTPUT_FILENAME = 'tables.txt'

if __name__ == '__main__':
    papers = {}
    for tetml_path in os.listdir(TETML_DIR):
        paper_id = tetml_path.replace('.tetml', '')
        tetml_path = os.path.join(TETML_DIR, tetml_path)
        try:
            with open(tetml_path, 'r') as f_tetml:
                print('Extracting tables from {}...'.format(paper_id))
                tables = TetmlTableExtractor.extract_tables(
                    tetml=BeautifulSoup(f_tetml),
                    caption_search_window=3)
                papers.update({paper_id: tables})
        except FileNotFoundError as e:
            print(e)
            print('{} missing TETML file. Skipping...'.format(paper_id))

    with open(os.path.join(DATA_DIR, OUTPUT_FILENAME), 'w') as f:
        for paper_id, tables in papers.items():
            f.write(paper_id + '\n')
            for table in tables:
                try:
                    f.write(str(table) + '\n\n\n\n\n')
                except Exception as e:
                    print(e)

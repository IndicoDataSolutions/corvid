"""

Example that extracts Tables from TETML files and saves them via Pickle

"""

import os

from bs4 import BeautifulSoup

from corvid.table_extraction.table_extractor import TetmlTableExtractor
try:
    import cPickle as pickle
except:
    import pickle

from config import TETML_DIR, PICKLE_DIR

IS_OVERWRITE = True

if __name__ == '__main__':
    papers = {}
    for tetml_path in os.listdir(TETML_DIR):
        paper_id = tetml_path.replace('.tetml', '')
        tetml_path = os.path.join(TETML_DIR, tetml_path)
        pickle_path = os.path.join(PICKLE_DIR, paper_id + '.pickle')

        if os.path.exists(pickle_path) and not IS_OVERWRITE:
            print('{} already exists. Skipping...'.format(pickle_path))
            continue

        try:
            with open(tetml_path, 'r') as f_tetml:
                print('Extracting tables from {}...'.format(paper_id))
                tables = TetmlTableExtractor.extract_tables(
                    tetml=BeautifulSoup(f_tetml),
                    caption_search_window=3)

                divider = '\n\n-----------------------------------------------\n\n'
                print(divider.join([str(table) for table in tables]))

                print('Pickling extracted tables for {}...'.format(paper_id))
                with open(pickle_path, 'wb') as f_pickle:
                    pickle.dump(tables, f_pickle)

                papers.update({paper_id: tables})
        except FileNotFoundError as e:
            print(e)
            print('{} missing TETML file. Skipping...'.format(paper_id))

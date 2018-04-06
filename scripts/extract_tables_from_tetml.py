"""

Example that extracts Tables from TETML files and saves them via Pickle

"""

import os
import argparse

from bs4 import BeautifulSoup

from corvid.table_extraction.table_extractor import TetmlTableExtractor
try:
    import cPickle as pickle
except:
    import pickle

from config import TETML_XML_DIR, TETML_PICKLE_DIR

DIVIDER = '\n\n-----------------------------------------------\n\n'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', type=str,
                        help='enter path to local directory containing TETML files')
    parser.add_argument('-o', '--output_dir', type=str,
                        help='enter path to local directory to save pickled Tables')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    args = parser.parse_args()

    # define input files
    tetml_dir = args.input_dir if args.input_dir else TETML_XML_DIR

    # define output files
    pickle_dir = args.output_dir if args.output_dir else TETML_PICKLE_DIR

    table_extractor = TetmlTableExtractor(target_dir=pickle_dir)

    # logs
    logs = {
        'num_extract_success': 0,
        'num_missing_tetml': 0,
        'num_unknown_error': 0
    }

    papers = {}
    for tetml_path in os.listdir(tetml_dir):
        paper_id = tetml_path.replace('.tetml', '')
        tetml_path = os.path.join(tetml_dir, tetml_path)
        pickle_path = os.path.join(pickle_dir, paper_id + '.pickle')

        if os.path.exists(pickle_path) and not args.overwrite:
            print('{} already exists. Skipping...'.format(pickle_path))
            continue

        try:
            with open(tetml_path, 'r') as f_tetml:
                print('Extracting tables from {}...'.format(paper_id))
                table_extractor.parse(
                    paper_id=paper_id,
                    source_xml_path=tetml_path
                )
                with open(pickle_path, 'rb') as f_pickle:
                    tables = pickle.load(f_pickle)

                print(DIVIDER.join([str(table) for table in tables]))

                papers.update({paper_id: tables})

                logs['num_extract_success'] += 1

        except FileNotFoundError as e:
            print(e)
            print('{} missing TETML file. Skipping...'.format(paper_id))

            logs['num_missing_tetml'] += 1

        except Exception as e:
            print(e)

            logs['num_unknown_error'] += 1

        print(DIVIDER)
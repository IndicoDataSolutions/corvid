"""

Retrieve JSONs from ElasticSearch API given a paperId
Get the pdflib xml or the tables in each of the List of CitedBy Papers 

"""

import os
import re
from bs4 import BeautifulSoup

from corvid.types.table import Table
from corvid.util.config import S3_PDFS_URL, ES_PROD_URL, ES_DEV_URL
from scripts.fetch_papers import read_one_json_from_es, fetch_jsons_from_es, \
    fetch_pdfs_from_s3
from scripts.parse_pdfs import parse_pdfs

basepath = os.path.dirname(__file__)

datasets_input_file = os.path.abspath(
    os.path.join(basepath, '..', 'input_dir', 'dataset.txt'))
tet_path = os.path.abspath(
    os.path.join(basepath, '..', '..', 'lib', 'tet', 'bin', 'tet'))


def files(path):
    """
    Utility function get valid files from a directory
    """
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


def count_number_datasets(self):
    number_of_datasets = 0
    with open(datasets_input_file, 'r') as f:
        for line in f:
            tokens = re.split(r'\t+', line.rstrip('\t\n'))
            dataset_paper_hash = tokens[1]

            # we do not have the paper id or the paper for some of the datasets
            if dataset_paper_hash != 'N/A':
                number_of_datasets += 1

    print(number_of_datasets, 'valid datasets were found in ',
          datasets_input_file)

count_number_datasets()


with open(datasets_input_file, 'r') as f:
    for line in f:
        tokens = re.split(r'\t+', line.rstrip('\t\n'))
        dataset_paper_hash = tokens[1]

        # we do not have the dataset paper id or dataset paper
        # identified for some of the datasets
        if dataset_paper_hash != 'N/A':
            print(dataset_paper_hash)
            try:
                print('Fetching dataset paper with Paper Id {}'.format(
                    dataset_paper_hash))
                dataset_paper = read_one_json_from_es(ES_PROD_URL,
                                                       dataset_paper_hash)

                # get list of papers that cite the dataset paper
                # TODO: we need some heuristics to get a more conservative
                # citedBy list e.g., ignore list citation
                citedBy = dataset_paper.get('citedBy')
                number_citedBy = len(citedBy)
                print('# of citedBy papers', number_citedBy)

                # we will need jsons of citedBy papers if we extract
                # other attributes to filer the papers or table downstream
                #fetch_jsons_from_es(ES_PROD_URL, citedBy, out_file)

                pdf_dir = os.path.abspath(
                    os.path.join(basepath, '..', 'output_dir', 'pdf',
                                 dataset_paper_hash))

                if not os.path.exists(pdf_dir):
                    os.makedirs(pdf_dir)

                pdf_dir = os.path.abspath(
                    os.path.join(pdf_dir, 'dataset_paper_hash'))

                fetch_pdfs_from_s3(S3_PDFS_URL, citedBy, pdf_dir)

                tetml_dir = os.path.abspath(
                    os.path.join(basepath, '..', 'output_dir', 'tetml',
                                 dataset_paper_hash))

                if not os.path.exists(tetml_dir):
                    os.makedirs(tetml_dir)

                # parse pdfs to tetml
                parse_pdfs(tet_path, pdf_dir, tetml_dir)

                for TETML_FILENAME in files(tetml_dir):
                    with open(os.path.join(tetml_dir, TETML_FILENAME),
                              'r') as tetf:
                        print('Reading TET file', tetml_dir, '/',
                              TETML_FILENAME)
                        xml = BeautifulSoup(tetf, 'lxml')
                        tables = []
                        for table_tetml in xml.find_all('table'):
                            try:
                                table = Table.from_bs4_tag(table_tetml)
                                print(table)
                                tables.append(table)
                            except Exception as e:
                                print(e)
                                print('Skipping some table in', tetml_dir, '/',
                                      TETML_FILENAME)
                tables = [Table.from_bs4_tag(table) for table in
                          xml.find_all('table')]

                for table in tables:
                 	print (table)

            except Exception as e:
                print(e)
                print('Skipping paper_id {}'.format(dataset_paper_hash))

            #delete the following line to let the loop
            # run over all the dataset papers
            exit()

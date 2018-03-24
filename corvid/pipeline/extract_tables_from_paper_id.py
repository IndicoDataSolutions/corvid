"""

Extracts as many tables as possible from a given paper

"""

import os

from typing import List

try:
    import cPickle as pickle
except:
    import pickle

from bs4 import BeautifulSoup

from corvid.types.table import Table
from corvid.pipeline.paper_fetcher import PaperFetcher, PaperFetcherException
from corvid.pipeline.pdf_parser import PDFParser, PDFParserException
from corvid.table_extraction.table_extractor import TetmlTableExtractor, TetmlTableExtractorException

class PipelineFetchPDFsException(Exception):
    pass

class PipelineParsePDFsException(Exception):
    pass

class PipelineExtractTablesException(Exception):
    pass

POSSIBLE_EXCEPTIONS = [PipelineFetchPDFsException, PipelineParsePDFsException, PipelineExtractTablesException]

# TODO: logging mechanism that counts different types of Exceptions
def extract_tables_from_paper_id(paper_id: str,
                                 pdf_fetcher: PaperFetcher,
                                 pdf_parser: PDFParser,
                                 target_table_dir: str) -> List[Table]:
    """

    Handles caching (i.e. if target_file already exists locally, skips fetching)

    """

    # fetch PDFs of relevant papers
    pdf_path = pdf_fetcher.get_target_path(paper_id)
    if not os.path.exists(pdf_path):
        try:
            pdf_fetcher.fetch(paper_id)
        except PaperFetcherException as e:
            print(e)
            raise PipelineFetchPDFsException


    # parse each PDF to XML
    xml_path = pdf_parser.get_target_path(paper_id)
    if not os.path.exists(xml_path):
        try:
            pdf_parser.parse(paper_id, source_pdf_path=pdf_path)
        except PDFParserException as e:
            print(e)
            raise PipelineParsePDFsException

    # TODO: consider moving file path management into table_extractor
    # extract tables from TETML or load if already exists
    pickle_path = '{}.pickle'.format(os.path.join(target_table_dir, paper_id))
    if not os.path.exists(pickle_path):
        try:
            with open(xml_path, 'r') as f_xml:
                tables = TetmlTableExtractor.extract_tables(
                    tetml=BeautifulSoup(f_xml),
                    paper_id=paper_id
                )
            with open(pickle_path, 'wb') as f_pickle:
                pickle.dump(tables, f_pickle)

        except TetmlTableExtractorException as e:
            print(e)
            raise PipelineExtractTablesException
    else:
        with open(pickle_path, 'rb') as f_pickle:
            tables = pickle.load(f_pickle)

    return tables



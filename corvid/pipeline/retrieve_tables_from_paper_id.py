"""

Retrieves as many tables as possible from a given paper.
Fetches resources or performs extraction, if necessary.

"""

import os

from typing import List

try:
    import cPickle as pickle
except ImportError:
    import pickle


from corvid.types.table import Table
from corvid.pipeline.paper_fetcher import Fetcher, FetcherException
from corvid.table_extraction.pdf_parser import PDFToXMLParser, PDFToXMLParserException
from corvid.table_extraction.table_extractor import TableExtractor, TableExtractorException

class PipelineFetchPDFsException(Exception):
    pass

class PipelineParsePDFsException(Exception):
    pass

class PipelineExtractTablesException(Exception):
    pass

POSSIBLE_EXCEPTIONS = [PipelineFetchPDFsException, PipelineParsePDFsException, PipelineExtractTablesException]

# TODO: logging mechanism that counts different types of Exceptions
def retrieve_tables_from_paper_id(paper_id: str,
                                  pdf_fetcher: Fetcher,
                                  pdf_parser: PDFToXMLParser,
                                  table_extractor: TableExtractor) -> List[Table]:
    """

    Handles caching (i.e. if target_file already exists locally, skips fetching)

    """

    # fetch PDFs of relevant papers
    pdf_path = pdf_fetcher.get_target_path(paper_id)
    if not os.path.exists(pdf_path):
        try:
            pdf_fetcher.fetch(paper_id)
        except FetcherException as e:
            print(e)
            raise PipelineFetchPDFsException

    # parse each PDF to some parsed output (e.g. XML)
    parse_output_path = pdf_parser.get_target_path(paper_id)
    if not os.path.exists(parse_output_path):
        try:
            pdf_parser.parse(paper_id, source_pdf_path=pdf_path)
        except PDFToXMLParserException as e:
            print(e)
            raise PipelineParsePDFsException

    # TODO: consider moving file path management into table_extractor
    # extract tables from XML or load if already exists
    pickle_path = table_extractor.get_target_path(paper_id)
    if not os.path.exists(pickle_path):
        try:
            table_extractor.extract(paper_id=paper_id,
                                    source_path=parse_output_path)
        except TableExtractorException as e:
            print(e)
            raise PipelineExtractTablesException

    # retrieve tables
    with open(pickle_path, 'rb') as f_pickle:
        tables = pickle.load(f_pickle)

    return tables



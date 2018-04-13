"""

Classes that extract as many Tables as possible from a local PDF.

"""

import os

from typing import List

try:
    import cPickle as pickle
except ImportError:
    import pickle

from corvid.types.table import Table

from corvid.table_extraction.pdf_to_xml_parser import PDFToXMLParser, \
    TetmlPDFToXMLParser, OmnipagePDFToXMLParser
from corvid.table_extraction.xml_to_tables_parser import XMLToTablesParser, \
    TetmlXMLToTablesParser, OmnipageXMLToTablesParser


class TableExtractor(object):
    def extract(self, paper_id: str, source_pdf_path: str, tables_pkl_path: str,
                *args, **kwargs) -> List[Table]:
        raise NotImplementedError

    # def fetch_and_extract(self, paper_id: str,
    #                       source_pdf_path: str,
    #                       tables_pkl_path: str,
    #                       fetcher: Fetcher, *args, **kwargs) -> List[Table]:
    #     """Extension of `extract` method that allows user to provide a
    #     (user-implemented) Fetcher object from which to fetch a remote
    #     PDF, if cant find one locally for extraction"""
    #     if not os.path.exists(source_pdf_path):
    #         fetcher.fetch(paper_id)
    #     tables = self.extract(paper_id, source_pdf_path, tables_pkl_path,
    #                           *args, **kwargs)
    #     return tables


class XMLTableExtractor(TableExtractor):
    def __init__(self,
                 pdf_to_xml_parser: PDFToXMLParser,
                 xml_to_tables_parser: XMLToTablesParser):
        self.pdf_to_xml_parser = pdf_to_xml_parser
        self.xml_to_tables_parser = xml_to_tables_parser

    def extract(self, paper_id: str,
                source_pdf_path: str,
                intermediate_xml_path: str,
                tables_pkl_path: str,
                is_use_xml_cache: bool = True,
                is_use_pkl_cache: bool = True,
                *args, **kwargs) -> List[Table]:
        """Returns Tables extracted from a PDF while caching intermediate
        steps like using an external tool to process PDF -> XML.
        """
        if is_use_xml_cache and os.path.exists(intermediate_xml_path):
            pass
        else:
            self.pdf_to_xml_parser.parse(source_pdf_path, intermediate_xml_path)

        if is_use_pkl_cache and os.path.exists(tables_pkl_path):
            with open(tables_pkl_path, 'rb') as f_pkl:
                tables = pickle.load(f_pkl)
        else:
            tables = self.xml_to_tables_parser.parse(intermediate_xml_path,
                                                     tables_pkl_path,
                                                     paper_id,
                                                     *args, **kwargs)
        return tables


class TetmlTableExtractor(XMLTableExtractor):
    def __init__(self, tet_bin_path: str):
        pdf_to_xml_parser = TetmlPDFToXMLParser(tet_bin_path)
        xml_to_tables_parser = TetmlXMLToTablesParser()
        super(TetmlTableExtractor, self).__init__(pdf_to_xml_parser,
                                                  xml_to_tables_parser)


class OmnipageTableExtractor(XMLTableExtractor):
    def __init__(self, omnipage_bin_path: str):
        pdf_to_xml_parser = OmnipagePDFToXMLParser(omnipage_bin_path)
        xml_to_tables_parser = OmnipageXMLToTablesParser()
        super(OmnipageTableExtractor, self).__init__(pdf_to_xml_parser,
                                                     xml_to_tables_parser)

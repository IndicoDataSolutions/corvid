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

from corvid.table_extraction.pdf_to_xml_parser import PDFToXMLParser
from corvid.table_extraction.xml_to_tables_parser import XMLToTablesParser


class TableExtractor(object):
    def extract(self, paper_id: str, source_pdf_path: str,
                *args, **kwargs) -> List[Table]:
        raise NotImplementedError


class OmnipageTableExtractor(TableExtractor):
    def __init__(self, xml_cache_dir: str, pkl_cache_dir: str):
        self.pdf_to_xml_parser = PDFToXMLParser(target_dir=xml_cache_dir)
        self.xml_to_tables_parser = XMLToTablesParser(target_dir=pkl_cache_dir)

    def extract(self, paper_id: str, source_pdf_path: str,
                is_use_xml_cache: bool = True, is_use_pkl_cache: bool = True,
                *args, **kwargs) -> List[Table]:

        source_xml_path = self.pdf_to_xml_parser.get_target_path(paper_id)
        if is_use_xml_cache and os.path.exists(source_xml_path):
            pass
        else:
            self.pdf_to_xml_parser.parse(paper_id, source_pdf_path)

        tables_pkl_path = self.xml_to_tables_parser.get_target_path(paper_id)
        if is_use_pkl_cache and os.path.exists(tables_pkl_path):
            with open(tables_pkl_path, 'rb') as f_pkl:
                tables = pickle.load(f_pkl)
        else:
            tables = self.xml_to_tables_parser.parse(paper_id, source_xml_path)

        return tables


"""

Classes that parse local PDF -> XML by subprocess to call external parsing tool.
Typical usage is within TableExtractor that utilizes external PDF parsing tools.

"""

import os
import subprocess


class PDFToXMLParserException(Exception):
    pass


class TetmlPDFToXMLParserException(PDFToXMLParserException):
    pass


class OmnipagePDFToXMLParserException(PDFToXMLParserException):
    pass


class PDFToXMLParser(object):
    def parse(self, source_pdf_path: str, target_xml_path: str):
        raise NotImplementedError


class TetmlPDFToXMLParser(PDFToXMLParser):
    def __init__(self, tet_bin_path: str):
        if not os.path.exists(tet_bin_path):
            raise FileNotFoundError('{} doesnt exist'.format(tet_bin_path))
        self.tet_bin_path = tet_bin_path

    def parse(self, source_pdf_path: str, target_xml_path: str):
        try:
            cmd = '{tet} --tetml wordplus --targetdir {targetdir} --outfile {tetml_filename} --pageopt {pageopt} --docopt checkglyphlists {pdf}' \
                .format(tet=self.tet_bin_path,
                        targetdir=os.path.dirname(target_xml_path),
                        tetml_filename=os.path.basename(target_xml_path),
                        pageopt='"vectoranalysis={structures=tables}"',
                        pdf=source_pdf_path)
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            if os.path.exists(target_xml_path):
                os.remove(target_xml_path)
            print(e)
            raise TetmlPDFToXMLParserException('TET failed to parse {}'
                                               .format(source_pdf_path))

class OmnipagePDFToXMLParser(PDFToXMLParser):
    def __init__(self, omnipage_bin_path: str):
        if not os.path.exists(omnipage_bin_path):
            raise FileNotFoundError('{} doesnt exist'.format(omnipage_bin_path))
        self.omnipage_bin_path = omnipage_bin_path

    def parse(self, source_pdf_path: str, target_xml_path: str):
        try:
            cmd = '{bin} -i {input_path} -o {output_path}' \
                .format(bin=self.omnipage_bin_path,
                        input_path=source_pdf_path,
                        output_path=target_xml_path)
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(e)
            raise OmnipagePDFToXMLParserException('OmniPage failed to parse {}'
                                                  .format(source_pdf_path))

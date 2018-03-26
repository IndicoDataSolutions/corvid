"""

Classes that calls local PDF -> XML parser via subprocess

"""


import os
import subprocess


class PDFParserException(Exception):
    pass

class TetmlPDFParserException(PDFParserException):
    pass

class OmnipagePDFParserException(PDFParserException):
    pass


class PDFParser(object):
    def __init__(self, target_dir: str):
        if not os.path.exists(target_dir):
            raise FileNotFoundError('Target directory {} doesnt exist'.format(target_dir))
        self.target_dir = target_dir

    def parse(self, paper_id: str, source_pdf_path: str) -> str:
        """Primary method for parsing a Paper's PDF given its id.
        Returns the local path of the XML output of the parsing.

        Raises exception unless user implements `_parse()`
        """
        target_path = self.get_target_path(paper_id)
        self._parse(paper_id, source_pdf_path, target_path)
        return target_path

    def _parse(self, paper_id: str, source_pdf_path: str, target_path: str):
        raise NotImplementedError

    def get_target_path(self, paper_id: str) -> str:
        raise NotImplementedError


class TetmlPDFParser(PDFParser):
    def __init__(self, tet_bin_path: str, target_dir: str):
        if not os.path.exists(tet_bin_path):
            raise TetmlPDFParserException('{} doesnt exist'.format(tet_bin_path))
        self.tet_bin_path = tet_bin_path

        super(TetmlPDFParser, self).__init__(target_dir)

    def _parse(self, paper_id: str, source_pdf_path: str, target_path: str):
        try:
            cmd = '{tet} --tetml wordplus --targetdir {targetdir} --pageopt {pageopt} --docopt checkglyphlists {pdf}' \
                .format(tet=self.tet_bin_path,
                        targetdir=self.target_dir,
                        pageopt='"vectoranalysis={structures=tables}"',
                        pdf=source_pdf_path)
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            if os.path.exists(target_path):
                os.remove(target_path)
            print(e)
            raise TetmlPDFParserException('TET failed to parse {}'.format(source_pdf_path))

    def get_target_path(self, paper_id: str) -> str:
        return '{}.tetml'.format(os.path.join(self.target_dir, paper_id))


class OmnipagePDFParser(PDFParser):
    def __init__(self, omnipage_bin_path: str, target_dir: str):
        if not os.path.exists(omnipage_bin_path):
            raise OmnipagePDFParserException('{} doesnt exist'.format(omnipage_bin_path))
        self.omnipage_bin_path = omnipage_bin_path

        super(OmnipagePDFParser, self).__init__(target_dir)

    def _parse(self, paper_id: str, source_pdf_path: str, target_path: str):
        try:
            cmd = '{bin} -i {input_path} -o {output_path}' \
                .format(bin=self.omnipage_bin_path,
                        input_path=source_pdf_path,
                        output_path=target_path)
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(e)
            raise OmnipagePDFParserException('OmniPage failed to parse {}'.format(source_pdf_path))

    def get_target_path(self, paper_id: str) -> str:
        return '{}.xml'.format(os.path.join(self.target_dir, paper_id))


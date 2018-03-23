"""

Classes that calls local PDF -> XML parser via subprocess

"""


import os
import subprocess


class TetmlPDFParserException(Exception):
    pass

class OmnipagePDFParserException(Exception):
    pass


class PDFParser(object):

    def __init__(self, source_dir: str, target_dir: str):

        if not os.path.exists(source_dir):
            raise FileNotFoundError('Source directory {} doesnt exist'.format(source_dir))
        self.source_dir = source_dir

        if not os.path.exists(target_dir):
            raise FileNotFoundError('Target directory {} doesnt exist'.format(target_dir))
        self.target_dir = target_dir


    def parse(self, paper_id: str) -> str:
        """Primary method for parsing a Paper's PDF given its id.
        Returns the local path of the XML output of the parsing.

        Raises exception unless user implements `_parse()`
        """

        source_path = os.path.join(self.source_dir, paper_id)
        target_path = os.path.join(self.target_dir, paper_id)
        self._parse(paper_id, source_path, target_path)
        return target_path

    def _parse(self, paper_id: str, source_path: str, target_path: str):
        raise NotImplementedError


class TetmlPDFParser(PDFParser):
    def __init__(self, tet_bin_path: str, source_dir: str, target_dir: str):


        if not os.path.exists(tet_bin_path):
            raise TetmlPDFParserException('{} doesnt exist'.format(tet_bin_path))
        self.tet_bin_path = tet_bin_path

        super(TetmlPDFParser, self).__init__(source_dir, target_dir)


    def _parse(self, paper_id: str, source_path: str, target_path: str):
        try:
            cmd = '{tet} --tetml wordplus --targetdir {targetdir} --pageopt {pageopt} --docopt checkglyphlists {pdf}' \
                .format(tet=self.tet_bin_path,
                        targetdir=self.target_dir,
                        pageopt='"vectoranalysis={structures=tables}"',
                        pdf=source_path)
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            os.remove(target_path)
            print(e)
            raise TetmlPDFParserException('TET failed to parse {}'.format(source_path))


class OmnipagePDFParser(PDFParser):
    pass




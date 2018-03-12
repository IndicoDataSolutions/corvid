"""

Parse raw PDFs using PDFlib's TET

"""

import argparse
import os

from config import TET_BIN_PATH, PDF_DIR, TETML_DIR
from corvid.util.tetml import parse_pdfs

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', default='pdflib', type=str,
                        help='currently only supports `pdflib`')
    parser.add_argument('-p', '--parser', type=str,
                        help='enter path to parser binary')
    parser.add_argument('-i', '--input_dir', type=str,
                        help='enter path to local directory containing pdfs')
    parser.add_argument('-o', '--output_dir', type=str,
                        help='enter path to local directory to save output tetml')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    args = parser.parse_args()

    OUTPUT_DIR = args.output_dir if args.output_dir else TETML_DIR
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if args.mode == 'pdflib':
        num_success, num_pdfs = \
            parse_pdfs(tet_path=args.parser if args.parser else TET_BIN_PATH,
                       pdf_dir=args.input_dir if args.input_dir else PDF_DIR,
                       out_dir=OUTPUT_DIR,
                       is_overwrite=args.overwrite)
        print('Successfully parsed {}/{} pdfs.'.format(num_success,
                                                       num_pdfs))
    else:
        raise NotImplementedError('Currently only supports `--mode pdflib`')

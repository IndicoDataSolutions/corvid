"""

Parse raw PDFs using PDFLib's TET

"""

import argparse
import os

from config import TET_BIN_PATH, PDF_DIR, TETML_DIR
from corvid.pipeline.pdf_parser import TetmlPDFParser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--parser', type=str,
                        help='enter path to parser binary')
    parser.add_argument('-i', '--input_dir', type=str,
                        help='enter path to local directory containing pdfs')
    parser.add_argument('-o', '--output_dir', type=str,
                        help='enter path to local directory to save output tetml')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    args = parser.parse_args()

    # define input files
    pdf_dir = args.input_dir if args.input_dir else PDF_DIR
    pdf_paths = [os.path.join(pdf_dir, path) for path in os.listdir(pdf_dir)]

    # define output directory
    output_dir = args.output_dir if args.output_dir else TETML_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # define parser
    pdf_parser = TetmlPDFParser(tet_bin_path=TET_BIN_PATH,
                                target_dir=output_dir)

    num_success = 0
    for pdf_path in pdf_paths:
        paper_id = os.path.basename(pdf_path).replace('.pdf', '')
        try:
            pdf_parser.parse(
                paper_id=paper_id,
                source_pdf_path=pdf_path
            )
            print('Parsed PDF {} to {}'.format(pdf_path, pdf_path))
            num_success += 1
        except Exception as e:
            print(e)
            print('Skipping PDF {}'.format(pdf_path))

    print('Successfully parsed {}/{} pdfs.'.format(num_success,
                                                   len(pdf_paths)))

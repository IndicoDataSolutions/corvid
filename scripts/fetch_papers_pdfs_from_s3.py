"""

Fetches remote Paper PDFs from S3 and saves to a directory

"""

import os
import argparse

from corvid.util.files import is_url_working, fetch_one_pdf_from_s3
from config import PAPER_IDS_TXT, PDF_DIR, S3_PDFS_URL, \
    convert_paper_id_to_s3_filename

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--paper_ids', type=str,
                        help='enter path to local file containing paper_ids')
    parser.add_argument('-i', '--input_url', type=str,
                        help='enter url containing remote files to fetch')
    parser.add_argument('-o', '--output_dir', type=str,
                        help='enter path to local directory to save PDFs')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    args = parser.parse_args()

    # TODO: allow a list of paper_ids or a file as input
    paper_ids_filename = args.paper_ids if args.paper_ids else PAPER_IDS_TXT
    with open(paper_ids_filename, 'r') as f:
        paper_ids = f.read().splitlines()

    # verify output filepath
    output_dir = args.output_dir if args.output_dir else PDF_DIR
    if os.path.exists(output_dir) and not args.overwrite:
        raise Exception('{} already exists'.format(output_dir))

    # verify S3 endpoint
    s3_url = args.input_url if args.input_url else S3_PDFS_URL
    if not is_url_working(url=s3_url):
        raise Exception('{} not working'.format(s3_url))

    papers = []
    num_success = 0
    for paper_id in paper_ids:
        try:
            fetch_one_pdf_from_s3(s3_url,
                                  paper_id,
                                  output_dir,
                                  convert_paper_id_to_s3_filename,
                                  args.overwrite)
            print('Fetched paper_id {}'.format(paper_id))
            num_success += 1
        except Exception as e:
            print(e)
            print('Skipping paper_id {}'.format(paper_id))

    print('Successfully fetched {}/{} PDFs.'.format(num_success,
                                                    len(paper_ids)))

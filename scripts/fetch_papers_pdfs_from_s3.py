"""

Fetches remote Paper PDFs from S3 and saves to a directory

"""

import os
import argparse

from corvid.pipeline.paper_fetcher import S3PDFPaperFetcher
from config import PDF_DIR, S3_PDFS_BUCKET

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--paper_ids', type=str,
                        help='enter path to local file containing paper_ids')
    parser.add_argument('-b', '--bucket', type=str,
                        help='enter name of bucket containing remote files to fetch')
    parser.add_argument('-o', '--output_dir', type=str,
                        help='enter path to local directory to save PDFs')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    args = parser.parse_args()

    paper_ids_filename = args.paper_ids
    with open(paper_ids_filename, 'r') as f:
        paper_ids = f.read().splitlines()

    # verify output filepath
    output_dir = args.output_dir if args.output_dir else PDF_DIR
    if os.path.exists(output_dir) and not args.overwrite:
        raise Exception('{} already exists'.format(output_dir))

    # TODO: add some endpoint verification
    s3_bucket = args.bucket if args.bucket else S3_PDFS_BUCKET

    pdf_fetcher = S3PDFPaperFetcher(bucket=S3_PDFS_BUCKET,
                                    target_dir=output_dir)

    papers = []
    num_success = 0
    for paper_id in paper_ids:
        try:
            pdf_path = pdf_fetcher.fetch(paper_id=paper_id)
            print('Fetched PDF {}'.format(pdf_path))
            num_success += 1
        except Exception as e:
            print(e)
            print('Skipping paper_id {}'.format(paper_id))

    print('Successfully fetched {}/{} PDFs.'.format(num_success,
                                                    len(paper_ids)))



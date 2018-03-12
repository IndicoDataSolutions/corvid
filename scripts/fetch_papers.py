"""

Functions that fetch remote files:

- Paper JSONs from ElasticSearch API
- Paper PDFs from S3

"""

import argparse

from corvid.util.files import is_url_working, fetch_jsons_from_es, \
    fetch_pdfs_from_s3
from config import PAPER_IDS_TXT, PAPERS_JSON, PDF_DIR, S3_PDFS_URL, \
    convert_paper_id_to_s3_filename, convert_paper_id_to_es_endpoint

try:
    from config import ES_PROD_URL as ES_URL
except:
    from config import ES_DEV_URL as ES_URL

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', required=True, type=str,
                        help='enter `json` or `pdf`')
    parser.add_argument('-p', '--paper_ids', type=str,
                        help='enter path to local file containing paper_ids')
    parser.add_argument('-i', '--input_url', type=str,
                        help='enter url containing remote files to fetch')
    parser.add_argument('-o', '--out_path', type=str,
                        help='enter path to local file/directory to save output file(s)')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    args = parser.parse_args()

    # TODO: allow a list of paper_ids or a file as input
    paper_ids_filename = args.paper_ids if args.paper_ids else PAPER_IDS_TXT
    with open(paper_ids_filename, 'r') as f:
        paper_ids = f.read().splitlines()

    if args.mode == 'json':
        if not is_url_working(url=ES_URL):
            raise Exception('{} not working'.format(ES_URL))

        fetch_jsons_from_es(
            es_url=args.input_url if args.input_url else ES_URL,
            paper_ids=paper_ids,
            out_file=args.out_path if args.out_path else PAPERS_JSON,
            convert_paper_id_to_es_endpoint=convert_paper_id_to_es_endpoint,
            is_overwrite=args.overwrite)

    elif args.mode == 'pdf':
        if not is_url_working(url=S3_PDFS_URL):
            raise Exception('{} not working'.format(S3_PDFS_URL))

        fetch_pdfs_from_s3(
            s3_url=args.input_url if args.input_url else S3_PDFS_URL,
            paper_ids=paper_ids,
            out_dir=args.out_path if args.out_path else PDF_DIR,
            convert_paper_id_to_s3_filename=convert_paper_id_to_s3_filename,
            is_overwrite=args.overwrite)

    else:
        raise Exception('Currently only supports `json` and `pdf` modes.')

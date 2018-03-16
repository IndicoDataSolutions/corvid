"""

Fetches remote Paper JSONs from ElasticSearch API and writes results
to a single output file containing a List[JSON]

"""

import os
import argparse
import json

from corvid.util.files import is_url_working, read_one_json_from_es
from config import convert_paper_id_to_es_endpoint

try:
    from config import ES_PROD_URL as ES_URL
except:
    from config import ES_DEV_URL as ES_URL

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--paper_ids', type=str,
                        help='enter path to local file containing paper_ids')
    parser.add_argument('-i', '--input_url', type=str,
                        help='enter url containing remote files to fetch')
    parser.add_argument('-o', '--output_path', type=str,
                        help='enter path to local file to save output file')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing file')
    args = parser.parse_args()

    # TODO: allow a list of paper_ids or a file as input
    paper_ids_filename = args.paper_ids
    with open(paper_ids_filename, 'r') as f:
        paper_ids = f.read().splitlines()

    # verify output filepath
    output_filepath = args.output_path
    if os.path.exists(output_filepath) and not args.overwrite:
        raise Exception('{} already exists'.format(output_filepath))

    # verify ES endpoint
    es_url = args.input_url if args.input_url else ES_URL
    assert is_url_working(url=es_url)

    papers = []
    num_success = 0
    for paper_id in paper_ids:
        try:
            papers.append(read_one_json_from_es(es_url,
                                                paper_id,
                                                convert_paper_id_to_es_endpoint))
            print('Fetched paper_id {}'.format(paper_id))
            num_success += 1
        except Exception as e:
            print(e)
            print('Skipping paper_id {}'.format(paper_id))

    with open(output_filepath, 'w') as f:
        json.dump(papers, f)
        print('Successfully fetched {}/{} JSONs.'.format(num_success,
                                                        len(paper_ids)))

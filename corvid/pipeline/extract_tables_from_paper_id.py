"""

Extracts as many tables as possible from a given paper

"""

import os

from corvid.util.files import fetch_one_pdf_from_s3

def extract_tables_from_paper_id(paper_id: str,
                                 pdf_path: str,
                                 ):
    """

    """

    # fetch PDFs of relevant papers
    if not os.path.exists(pdf_path):
        try:
            fetch_one_pdf_from_s3(
                s3_bucket=S3_PDFS_BUCKET,
                paper_id=paper_id,
                out_dir=PDF_DIR,
                convert_paper_id_to_s3_filename=convert_paper_id_to_s3_filename,
                is_overwrite=True)
        except Exception as e:
            print(e)

    # parse each PDF to TETML
    tetml_path = '{}.tetml'.format(os.path.join(TETML_DIR, paper_id))
    if not os.path.exists(tetml_path):
        try:
            output_path = parse_one_pdf(tet_path=TET_BIN_PATH,
                                       pdf_path=pdf_path,
                                       out_dir=TETML_DIR,
                                       is_overwrite=True)
        except Exception as e:
            print(e)


    # extract tables from TETML or load if already exists
    pickle_path = '{}.pickle'.format(os.path.join(PICKLE_DIR, paper_id))
    if not os.path.exists(pickle_path):
        try:
            with open(tetml_path, 'r') as f_tetml:
                tables = TetmlTableExtractor.extract_tables(
                    tetml=BeautifulSoup(f_tetml),
                    paper_id=paper_id,
                    caption_search_window=CAPTION_SEARCH_WINDOW)
            with open(pickle_path, 'wb') as f_pickle:
                pickle.dump(tables, f_pickle)

        except Exception as e:
            print(e)

    else:
        with open(pickle_path, 'rb') as f_pickle:
            tables = pickle.load(f_pickle)

    return tables


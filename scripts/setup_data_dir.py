"""

Setup data directories

"""

import os
from config import DATA_DIR, \
    JSON_DIR, \
    PDF_DIR, \
    TETML_DIR, TETML_XML_DIR, TETML_PICKLE_DIR, \
    OMNIPAGE_DIR, OMNIPAGE_XML_DIR, OMNIPAGE_PICKLE_DIR


if __name__ == '__main__':
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)

    if not os.path.exists(JSON_DIR):
        os.mkdir(JSON_DIR)

    if not os.path.exists(PDF_DIR):
        os.mkdir(PDF_DIR)

    if not os.path.exists(TETML_DIR):
        os.mkdir(TETML_DIR)

    if not os.path.exists(TETML_XML_DIR):
        os.mkdir(TETML_XML_DIR)

    if not os.path.exists(TETML_PICKLE_DIR):
        os.mkdir(TETML_PICKLE_DIR)

    if not os.path.exists(OMNIPAGE_DIR):
        os.mkdir(OMNIPAGE_DIR)

    if not os.path.exists(OMNIPAGE_XML_DIR):
        os.mkdir(OMNIPAGE_XML_DIR)

    if not os.path.exists(OMNIPAGE_PICKLE_DIR):
        os.mkdir(OMNIPAGE_PICKLE_DIR)
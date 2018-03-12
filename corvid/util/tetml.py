"""

Miscellaneous functions for working with PDFLib's TETML PDF-parsing tool

"""

import os
import subprocess

from typing import Tuple


def parse_one_pdf(tet_path: str,
                  pdf_path: str,
                  out_dir: str,
                  is_overwrite: bool = False) -> str:
    """Wrapper around TETML command line call to parse PDF into TETML format
    with optimal settings for table extraction application.

    Returns path of newly-created TETML file.
    """
    tetml_path = os.path.join(out_dir,
                              os.path.basename(pdf_path).replace('.pdf',
                                                                 '.tetml'))
    if os.path.exists(tetml_path) and not is_overwrite:
        raise Exception('{} already exists'.format(tetml_path))

    try:
        cmd = '{tet} --tetml wordplus --targetdir {out} --pageopt {option} --docopt checkglyphlists {pdf}' \
            .format(tet=tet_path,
                    out=out_dir,
                    option='"vectoranalysis={structures=tables}"',
                    pdf=pdf_path)
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        os.remove(tetml_path)
        print(e)
        raise Exception('TETML failed to parse {}'.format(pdf_path))

    return tetml_path


def parse_pdfs(tet_path: str, pdf_dir: str, out_dir: str,
               is_overwrite: bool = False) -> Tuple[int, int]:
    pdf_paths = [os.path.join(pdf_dir, path) for path in os.listdir(pdf_dir)]
    num_success = 0
    for pdf in pdf_paths:
        try:
            print('Parsing PDF {}'.format(pdf))
            parse_one_pdf(tet_path, pdf, out_dir, is_overwrite)
            num_success += 1
        except Exception as e:
            print(e)
            print('Skipping PDF {}'.format(pdf))
    return num_success, len(pdf_paths)

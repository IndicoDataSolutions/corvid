"""

Parse raw PDFs using PDFlib's TET

"""

import os
import subprocess


def parse_one_pdf(tet_path: str, pdf_path: str, out_dir: str,
                  is_overwrite: str = False):
    tetml_path = os.path.join(out_dir,
                              os.path.basename(pdf_path).replace('.pdf',
                                                                 '.tetml'))
    if os.path.exists(tetml_path) and not is_overwrite:
        raise Exception('{} already exists'.format(tetml_path))

    try:
        cmd = '{} --tetml word --targetdir {} --pageopt {} {}' \
            .format(tet_path,
                    out_dir,
                    '"vectoranalysis={structures=tables}"',
                    pdf_path)
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        os.remove(tetml_path)
        print(e)
        raise Exception('TETML failed to parse {}'.format(pdf_path))


def parse_pdfs(tet_path: str, pdf_dir: str, out_dir: str,
               is_overwrite: str = False):
    pdf_paths = [os.path.join(pdf_dir, path) for path in os.listdir(pdf_dir)]
    for pdf in pdf_paths:
        try:
            print('Parsing PDF {}'.format(pdf))
            parse_one_pdf(tet_path, pdf, out_dir, is_overwrite)
        except Exception as e:
            print(e)
            print('Skipping PDF {}'.format(pdf))

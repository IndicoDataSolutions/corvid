"""

Parse raw PDFs using PDFlib's TET

"""

import argparse
import os
import subprocess

from typing import Tuple


def parse_one_pdf(tet_path: str, pdf_path: str, out_dir: str,
                  is_overwrite: str = False):
    tetml_path = os.path.join(out_dir,
                              os.path.basename(pdf_path).replace('.pdf',
                                                                 '.tetml'))
    if os.path.exists(tetml_path) and not is_overwrite:
        raise Exception('{} already exists'.format(tetml_path))

    try:
        cmd = '{tet} --tetml wordplus --targetdir {out} --pageopt {option} {pdf}' \
            .format(tet=tet_path,
                    out=out_dir,
                    option='"vectoranalysis={structures=tables}"',
                    pdf=pdf_path)
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        os.remove(tetml_path)
        print(e)
        raise Exception('TETML failed to parse {}'.format(pdf_path))


def parse_pdfs(tet_path: str, pdf_dir: str, out_dir: str,
               is_overwrite: str = False) -> Tuple[int, int]:
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', default='pdflib', type=str,
                        help='currently only supports `pdflib`')
    parser.add_argument('-p', '--parser', required=True, type=str,
                        help='enter path to parser binary')
    parser.add_argument('-i', '--input_dir', required=True, type=str,
                        help='enter path to local input')
    parser.add_argument('-o', '--output_dir', required=True, type=str,
                        help='enter path to local output')
    parser.add_argument('--is_overwrite', type=bool, default=False,
                        help='enter True or False for overwrite existing files')
    args = parser.parse_args()

    if args.mode == 'pdflib':
        num_success, num_pdfs = parse_pdfs(tet_path=args.parser,
                                           pdf_dir=args.input_dir,
                                           out_dir=args.output_dir,
                                           is_overwrite=args.is_overwrite)
        print('Successfully parsed {}/{} pdfs.'.format(num_success,
                                                       num_pdfs))
    else:
        raise NotImplementedError('Currently only supports `--mode pdflib`')


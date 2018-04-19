"""

"""

import argparse

try:
    import cPickle as pickle
except:
    import pickle

DIVIDER = '\n\n-----------------------------------------------\n\n'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_pkl_path', type=str,
                        help='enter path to local pickle file containing Tables')
    args = parser.parse_args()

    with open(args.input_pkl_path, 'rb') as f_pkl:
        tables = pickle.load(f_pkl)

    print(DIVIDER.join([str(table) for table in tables]))

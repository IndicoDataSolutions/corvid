
import argparse

def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('paper_id', type=str)
    parser.add_argument('--url', type=str)
    parser.add_argument('--port', type=str)
    return parser.parse_args(args)


import argparse
import boto3

def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('paper_id', type=str)
    parser.add_argument('--es_url', type=str)
    return parser.parse_args(args)

def read_from_s3(bucket, filename):
    # s3_client = boto3.client('s3')
    pass

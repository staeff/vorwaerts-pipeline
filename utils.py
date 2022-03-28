from pathlib import Path
import logging
import boto3
from botocore.exceptions import ClientError
import os
import sys

def create_path(path_name):
    """
    Create path_name path if it does not exist
    """
    cwd = Path.cwd()
    dirname = cwd / path_name
    if not dirname.exists():
        print(f"Creating {dirname}")
        os.makedirs(dirname, exist_ok=True)
    return dirname

def get_s3_bucket(bucket_name):
    """Connect to a s3 bucket for further operations"""
    s3 = boto3.resource('s3')
    return s3.Bucket(bucket_name)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv

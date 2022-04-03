from pathlib import Path
import boto3
import os
import sys
from dotenv import load_dotenv
from distutils.util import strtobool

load_dotenv()
USE_AWS = strtobool(os.getenv("USE_AWS", "False"))
AWS_AD_IMAGES_BUCKET = os.getenv("AWS_AD_IMAGES_BUCKET")
AWS_DATA_BUCKET = os.getenv("AWS_DATA_BUCKET")
AWS_IMAGES_BUCKET = os.getenv("AWS_IMAGES_BUCKET")
AWS_BUCKETS = (AWS_AD_IMAGES_BUCKET, AWS_DATA_BUCKET, AWS_IMAGES_BUCKET)


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


def get_existing_buckets(s3):
    """Getting existing buckets from s3"""
    response = s3.list_buckets()
    existing_buckets = [bucket["Name"] for bucket in response["Buckets"]]
    return existing_buckets


def create_s3_bucket(s3, bucket_name):
    """Create a bucket on s3"""
    location = {"LocationConstraint": "eu-central-1"}
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)


def check_s3():
    """Check if all buckets exist on s3 or create them"""
    s3 = boto3.client("s3")
    existing_buckets = get_existing_buckets(s3)
    for bucket_name in AWS_BUCKETS:
        if bucket_name not in existing_buckets:
            create_s3_bucket(s3, bucket_name)


def delete_objects_in_bucket(s3bucket):
    """Deletes all the objects in a s3 bucket"""
    for s3_object in s3bucket.objects.all():
        s3_object.delete()


def delete_s3():
    """Deleting s3 buckets and content"""
    for bucket_name in AWS_BUCKETS:
        s3bucket = get_s3_bucket(bucket_name)
        delete_objects_in_bucket(s3bucket)
        s3bucket.delete()


def list_s3():
    """Show content for configured s3 buckets"""
    for bucket_name in AWS_BUCKETS:
        s3bucket = get_s3_bucket(bucket_name)
        print(f"Bucket: {bucket_name}")
        for obj in s3bucket.objects.all():
            print(f"-- {obj.key}")


def get_s3_bucket(bucket_name):
    """Connect to a s3 bucket for further operations"""
    s3 = boto3.resource("s3")
    return s3.Bucket(bucket_name)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        param = sys.argv[1]
    if USE_AWS and param == "check_s3":
        check_s3()
    if USE_AWS and param == "list_s3":
        list_s3()
    if USE_AWS and param == "delete_s3":
        delete_s3()

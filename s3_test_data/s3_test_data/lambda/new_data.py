import os

import boto3
from fastcore.net import HTTP404NotFoundError
from ghapi.all import GhApi

s3 = boto3.client("s3")


def handler(event, context):
    upload_bucket = os.environ["UPLOAD_BUCKET_NAME"]
    download_bucket = os.environ["DOWNLOAD_BUCKET_NAME"]

    new_data_key = event["Records"][0]["s3"]["object"]["key"]

    current_data_key = "test_data.tar.gz"

    print("Working...")
    try:
        download_bucket_contents = s3.list_objects_v2(Bucket=download_bucket)[
            "Contents"
        ]
        download_bucket_keys = [obj["Key"] for obj in download_bucket_contents]
    except KeyError:
        download_bucket_keys = []
    print("Got bucket contents.")

    if current_data_key in download_bucket_keys:
        print("Moving old data...")
        s3.copy_object(
            Bucket=download_bucket,
            CopySource={"Bucket": download_bucket, "Key": current_data_key},
            Key="test_data_old.tar.gz",
        )
        s3.delete_object(Bucket=download_bucket, Key=current_data_key)

    print("Moving new data...")
    s3.copy_object(
        Bucket=download_bucket,
        CopySource={"Bucket": upload_bucket, "Key": new_data_key},
        Key=current_data_key,
    )
    s3.delete_object(Bucket=upload_bucket, Key=new_data_key)

    print("Removing old data...")
    s3.delete_object(Bucket=download_bucket, Key="test_data_old.tar.gz")

    try:
        invalidate_github_cache()
    except HTTP404NotFoundError:
        print("Cache key test-data not found in GitHub actions cache")

    print("Done")


def invalidate_github_cache():
    repo_owner = os.environ["REPO_OWNER"]
    repo_name = os.environ["REPO_NAME"]
    github_access_token = os.environ["GITHUB_ACCESS_TOKEN"]

    gh = GhApi(owner=repo_owner, repo=repo_name, token=github_access_token)
    gh.actions.delete_actions_cache_by_key("test-data")

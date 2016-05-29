#!/usr/bin/env python

"""
A handy script that will deploy dgs3.fish to s3
"""
from __future__ import print_function

import argparse
import json
import mimetypes
import os

import boto3

INDEX = "index.html"
ERROR = "index.html"

def get_website_config():
    """Gets the website config"""
    config = {"ErrorDocument": {"Key": INDEX},
              "IndexDocument": {"Suffix": ERROR},
             }
    return config

def get_bucket_policy(bucket):
    """Gets the bucket policy"""
    # This bucket policy should allow for all objects in this bucket to be
    # accessible
    bucket_policy = {"Version": "2012-10-17",
                     "Statement": [{"Sid": "AddPerm",
                                    "Effect": "Allow",
                                    "Principal": "*",
                                    "Action": ["s3:GetObject"],
                                    "Resource": "arn:aws:s3:::{}/*"\
                                                                .format(bucket)}]
                    }
    bucket_policy_str = json.dumps(bucket_policy)
    return bucket_policy_str

def upload_site(bucket):
    """
    Uploads a site rooted at site_root into an S3 bucket.
    """
    client = boto3.client("s3")
    site_root = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "site")
    print("Setting bucket policy")
    bucket_policy = get_bucket_policy(bucket)
    client.put_bucket_policy(Bucket=bucket, Policy=bucket_policy)
    assert INDEX in os.listdir(site_root)
    assert ERROR in os.listdir(site_root)
    print("Converting bucket {} to be a website".format(bucket))
    site_config = get_website_config()
    client.put_bucket_website(Bucket=bucket,
                              WebsiteConfiguration=site_config)
    for _file in os.listdir(site_root):
        # We don't want to post hidden files (i.e. *.swp)
        if _file.startswith("."):
            continue
        full_path = os.path.join(site_root, _file)
        mime_type = mimetypes.guess_type(full_path)[0]
        print("Putting {}".format(full_path))
        with open(full_path, "rb") as _filep:
            client.put_object(Bucket=bucket,
                              Body=_filep,
                              ContentType=mime_type,
                              Key=_file)

def main():
    """The Main"""
    parser = argparse.ArgumentParser("Script to deploy dgs3.fish "
                                     "to an S3 bucket")
    parser.add_argument("bucket",
                        help="The bucket to deploy the site to")
    args = parser.parse_args()
    upload_site(args.bucket)

if __name__ == "__main__":
    main()

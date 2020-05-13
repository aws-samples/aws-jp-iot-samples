# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import base64
import datetime
import json
import logging
import os
import uuid

import boto3
import requests
from requests_aws4auth import AWS4Auth


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get Elasticsearch service settings from environmental variables
es_url = os.getenv("ES_URL")
region = os.getenv("REGION")

# Get credentials
credentials = boto3.Session().get_credentials()
aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es', session_token=credentials.token)


def process_record(record):
    """ Submit face recognition result to Elasticsearch service """
    payload = json.loads(base64.b64decode(record['kinesis']['data']))
    logger.info(f"record: {payload}")

    unix_time = payload["InputInformation"]["KinesisVideo"]["ServerTimestamp"]
    timestamp = datetime.datetime.utcfromtimestamp(unix_time).strftime("%Y-%m-%dT%H:%M:%S+0000")

    for face in payload["FaceSearchResponse"]:
        if not face["MatchedFaces"]:
            continue
        confidence = face["MatchedFaces"][0]["Similarity"]
        name = face["MatchedFaces"][0]["Face"]["ExternalImageId"]

        data = {"timestamp": timestamp, "name": name, "confidence": confidence}
        response = requests.post(f"{es_url}/record/face/{uuid.uuid4()}",
                                 auth=aws_auth,
                                 headers={"Content-Type": "application/json"},
                                 data=json.dumps(data))
        logger.info(f"result: code={response.status_code}, response={response.text}")


def lambda_handler(event, context):
    for record in event['Records']:
        process_record(record)
    return {"result": "ok"}

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import greengrasssdk
import json
import logging
import sys
import os

VALUE = os.environ.get('VALUE', '0.3')

# Setup logging to stdout
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Creating a greengrass core sdk client
client = greengrasssdk.client("iot-data")

def lambda_handler(event, context):
    logging.info(event)
    if float(event["value"]) > float(VALUE):
        client.publish(
            topic="alert/world",
            payload=json.dumps({"status": "alert", "value": event["value"]})
        )
        logging.warning("published alert")
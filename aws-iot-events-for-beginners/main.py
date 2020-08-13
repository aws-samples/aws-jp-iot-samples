# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from __future__ import absolute_import
from __future__ import print_function

import argparse
import json
import logging
import os
import random
import signal
import sys
import time
import traceback
from datetime import datetime

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# - Overview -
# This sample shows 1) how to connect AWS IoT Core. 2) How to publish

BASE_TOPIC = "data/"
DEFAULT_WAIT_TIME = 5
KEEPALIVE = 300

mqtt_connection = None
device_name = None

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.basicConfig()


def arg_check():
    """
    argument check
    """

    logging.debug("start: arg_check")
    parser = argparse.ArgumentParser()
    parser.add_argument("--device_name", required=True,
                        help="[Must], input config file. include path")
    parser.add_argument("--endpoint", required=True,
                        help="[Must], AWS IoT endpoint URI")
    parser.add_argument("--root_ca", required=False,
                        help="root ca file name with path")
    parser.add_argument("--cert", required=False,
                        help="device cert file name with path")
    parser.add_argument("--private", required=False,
                        help="private cert key file name with path")
    parser.add_argument('--verbosity', choices=[x.name for x in io.LogLevel],
                        default=io.LogLevel.NoLogs.name, help='Logging level')

    args = parser.parse_args()

    log_level = getattr(io.LogLevel, args.verbosity, "error")
    io.init_logging(log_level, 'stderr')
    loglevel_map = [
        logging.INFO, logging.INFO, logging.INFO,
        logging.INFO, logging.INFO, logging.DEBUG,
        logging.DEBUG]
    logger.setLevel(loglevel_map[log_level])
    logging.basicConfig()

    cert_list = find_certs_file()
    if args.root_ca is not None:
        cert_list[0] = args.root_ca
    if args.private is not None:
        cert_list[1] = args.private
    if args.cert is not None:
        cert_list[2] = args.cert

    logging.debug(cert_list)
    file_exist_check(cert_list)

    init_dict = {
        "device_name": args.device_name,
        "endpoint": args.endpoint,
        "certs": cert_list
    }
    return init_dict


def file_exist_check(cert_list):
    """
    Check the files exists
    all certs must placed in ./certs directory

    Parameters
    ----------
    cert_list: Array
    """

    for file in cert_list:
        if not os.path.exists(file):
            # if file not found, raise
            logger.error("cert file not found:%s", file)
            raise RuntimeError("file_not_exists")


def find_certs_file():
    """
    Find the certificates file from ./certs directory

    Returns
    ----------
    file_list: Array
        0: Root CA Cert, 1: private key, 2: certificate
    """

    certs_dir = "./certs"
    file_list = ["AmazonRootCA1.pem", "private.pem", "certificate.crt"]
    for _, _, names in os.walk(certs_dir):
        for file in names:
            if "AmazonRootCA1.pem" in file:
                file_list[0] = certs_dir + "/" + file
            elif "private" in file:
                file_list[1] = certs_dir + "/" + file
            elif "certificate" in file:
                file_list[2] = certs_dir + "/" + file

    return file_list

def device_main():
    """
    main loop for dummy device
    """
    global device_name, mqtt_connection

    init_info = arg_check()
    device_name = init_info['device_name']
    iot_endpoint = init_info['endpoint']
    rootca_file = init_info['certs'][0]
    private_key_file = init_info['certs'][1]
    certificate_file = init_info['certs'][2]

    logger.info("device_name: %s", device_name)
    logger.info("endpoint: %s", iot_endpoint)
    logger.info("rootca cert: %s", rootca_file)
    logger.info("private key: %s", private_key_file)
    logger.info("certificate: %s", certificate_file)

    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=iot_endpoint,
        cert_filepath=certificate_file,
        pri_key_filepath=private_key_file,
        client_bootstrap=client_bootstrap,
        ca_filepath=rootca_file,
        client_id=device_name,
        clean_session=False,
        keep_alive_secs=KEEPALIVE)

    connected_future = mqtt_connection.connect()

    # Start sending dummy data
    topic = BASE_TOPIC + device_name
    logging.info("topic: %s", topic)
    while True:
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        tmp = 20 + random.randint(-5, 5)
        payload = {"DEVICENAME": device_name, "TIMESTAMP": now, "VALUE": tmp}
        logger.debug("  payload: %s", payload)

        mqtt_connection.publish(
            topic=topic,
            payload=json.dumps(payload),
            qos=mqtt.QoS.AT_LEAST_ONCE)

        time.sleep(DEFAULT_WAIT_TIME)


def exit_sample(msg_or_exception):
    """
    Exit sample with cleaning

    Parameters
    ----------
    msg_or_exception: str or Exception
    """
    if isinstance(msg_or_exception, Exception):
        logger.error("Exiting sample due to exception.")
        traceback.print_exception(msg_or_exception.__class__, msg_or_exception, sys.exc_info()[2])
    else:
        logger.info("Exiting: %s", msg_or_exception)

    if not mqtt_connection:
        logger.info("Disconnecting...")
        mqtt_connection.disconnect()
    sys.exit(0)


def exit_handler(_signal, frame):
    """
    Exit sample
    """
    exit_sample(" Key abort")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_handler)

    device_main()

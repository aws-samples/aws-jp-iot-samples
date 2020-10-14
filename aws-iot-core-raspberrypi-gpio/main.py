#!/usr/bin/env python3

# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import json
import time

import RPi.GPIO as GPIO
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def read_switch():
    """ return True if switch is pressed """
    switch_pressed = GPIO.input(PIN) == GPIO.HIGH
    return switch_pressed


def main():
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint="xxxxxxxxxxx-ats.iot.region.amazonaws.com",
        cert_filepath="xxxxxxxxxx-certificate.pem.crt",
        pri_key_filepath="xxxxxxxxxx-private.pem.key",
        ca_filepath="AmazonRootCA1.pem",
        client_id="raspi_switch",
        client_bootstrap=client_bootstrap,
    )

    # Connect to AWS IoT
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("Connected!")

    # Read the switch state and publish a message
    last_state = False
    while True:
        switch_pressed = read_switch()
        if switch_pressed != last_state:
            print(f"pressed: {switch_pressed}")
            msg = {"pressed": switch_pressed}
            mqtt_connection.publish(
                topic="data/raspi_switch",
                payload=json.dumps(msg),
                qos=mqtt.QoS.AT_LEAST_ONCE)
        last_state = switch_pressed
        time.sleep(0.01)


if __name__ == '__main__':
    main()

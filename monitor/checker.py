#!/usr/bin/python3
"monitor application"

import sys
import getopt
import datetime
import re
import json
import requests
import yaml

from kafka import KafkaProducer
from kafka import KafkaConsumer

# the common functions for both apps
import monitor.monitorshared as m

def connect_kafka(conf):
    "connect to the kafka cluster"

    # first we need to check if the cluster has the topic setup
    try:
        KafkaClient = KafkaConsumer(bootstrap_servers=conf.kafka_broker,
                                    security_protocol="SSL",
                                    ssl_cafile=conf.kafka_SSL_CA,
                                    ssl_certfile=conf.kafka_SSL_cert,
                                    ssl_keyfile=conf.kafka_SSL_key,
                                    )
    except:
        m.error_print("can't connect to Kafka - please check the configuration")
        sys.exit(1)

    if conf.kafka_topic not in KafkaClient.topics():
        m.error_print("The Kafka cluster does not have the topic \"" + conf.kafka_topic
                      + "\". Please add it or change the config.")
        sys.exit(1)

    KafkaClient.close()

    # found on https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka ;-)
    # https://github.com/msgpack/msgpack-python for serialization
    try:
        KafkaProducerHandle = KafkaProducer(
            bootstrap_servers=conf.kafka_broker,
            security_protocol="SSL",
            ssl_cafile=conf.kafka_SSL_CA,
            ssl_certfile=conf.kafka_SSL_cert,
            ssl_keyfile=conf.kafka_SSL_key,
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        )
    except:
        m.error_print("can't connect to Kafka - please check the configuration")
        sys.exit(1)

    m.if_debug_print("connected to kafka: {}".format(conf.kafka_broker), conf)

    return KafkaProducerHandle

def check_host(target, conf):
    "take Target object and check"

    m.if_debug_print("check_host called for {}".format(target.name), conf)

    # record the time when we do the check
    target.checktime = int(datetime.datetime.utcnow().timestamp())

    # we are lazy and only check if it starts with http
    # TODO have a full regex and sanity check?
    if not re.match(r'^http', target.host):
        target.host = 'https://'+target.host

    # do the check
    # TODO: we set the timeout to 2 seconds, should be a per-host/config setting?
    try:
        http_request = requests.get(target.host, timeout=2)

    except requests.Timeout:
        target.return_code = 999
        target.response_time = 0
        m.if_debug_print("checking {} times out".format(target.host), conf)
        return
    except requests.ConnectionError:
        target.return_code = 999
        target.response_time = 0
        m.if_debug_print("Connection error checking {}".format(target.host), conf)
        return
    except:
        target.return_code = 999
        target.response_time = 0
        m.if_debug_print("Error checking {}".format(target.host), conf)
        return

    target.return_code = http_request.status_code

    # convert the miliseconds into int
    target.response_time = int(http_request.elapsed.total_seconds()*1000000)

    # if a regex is set
    if target.regex is not None:
        body_text = http_request.text

        # search for the regex in the whole file, count hits
        # TODO we could possible do this more elegant
        hits = re.findall(target.regex, body_text)
        for _ in hits:
            target.regex_hits += 1
    m.if_debug_print("check returned: {}".format(str(vars(target))), conf)

def fill_targets(target_list, conf):
    "read the yaml targets and fill the target objects"

    try:
        with open(conf.path_target_list, 'r') as fh_target_list:
            yaml_entries = yaml.safe_load(fh_target_list)

    # TODO should be more detailed perror()
    except yaml.YAMLError as exc:
        m.error_print("error {} opening list of targets: >{}<".
                      format(str(exc),
                             conf.path_target_list),
                      conf)
        sys.exit(1)

    # we iterate through the YAML entries and append another object
    # to an array of objects
    for name, rest in yaml_entries.items():
        target_list.append(m.Targets(name,
                                     str(rest['host'].strip()),
                                     str(rest['regex']).strip()))

    return target_list

def write_results(target, KafkaHandle, conf):
    "write Target object to Kafka"

    m.if_debug_print(json.dumps(target.__dict__), conf)
    KafkaHandle.send(conf.kafka_topic, json.dumps(target.__dict__))

    # Force sending of all messages
    KafkaHandle.flush()

def main(argv=None):
    "main"

    config_file = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:c:")
    except getopt.GetoptError:
        print('consumntodb.py -i <clinet_num>')
        sys.exit(2)
    for opt, args in opts:
        if opt == '-c':
            config_file = args


    # read config
    conf = m.Configuration(config_file, "checker")

    # prepare the array for all the Target objects
    targets = []

    # parse targets.yaml
    targets = fill_targets(targets, conf)
    target_num = len(targets)

    if target_num == 0:
        m.error_print("no targets found, exiting", conf)
        sys.exit(1)

    m.if_debug_print(str(target_num) + " targets", conf)

    # get connected to Kafka
    KafkaHandle = connect_kafka(conf)

    # iterate through the target array and check each and write out the result
    for entry in targets:
        check_host(entry, conf)
        write_results(entry, KafkaHandle, conf)

if __name__ == "__main__":
    main(sys.argv[1:])

#!/usr/bin/python3

import sys
import getopt
import json
from kafka import KafkaConsumer
import psycopg2

import monitor.monitorshared as m

def connect_db(conf):
    "connect to Postgres"
    db_connection = psycopg2.connect(
        database=conf.db_schema,
        user=conf.db_user,
        password=conf.db_passwd,
        host=conf.db_host,
        port=conf.db_port,
    )

    m.if_debug_print("Database connected {}".format(conf.db_host), conf)

    return db_connection

def connect_kafka(conf, client_num):
    "connect to Kafka"
    handle = KafkaConsumer(
        conf.kafka_topic,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        bootstrap_servers=conf.kafka_broker,
        security_protocol="SSL",
        ssl_cafile=conf.kafka_SSL_CA,
        ssl_certfile=conf.kafka_SSL_cert,
        ssl_keyfile=conf.kafka_SSL_key,
        client_id="postgres-client-"+str(client_num),
        group_id="postgres-consumer",
        value_deserializer=lambda x: json.loads(x).encode("utf-8"),
    )

    m.if_debug_print("connected to kafka: {}".format(conf.kafka_broker), conf)

    return handle

def main(argv):
    "main"

    client_num = 1
    config_file = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:c:")
    except getopt.GetoptError:
        print('consumntodb.py -i <clinet_num>')
        sys.exit(2)
    for opt, args in opts:
        if opt == '-c':
            config_file = args
        elif opt == "-i":
            client_num = args

    conf = m.Configuration(config_file, "PostgresConsumer")

    # connect to kafka and DB
    db_connection = connect_db(conf)
    kafka_handle = connect_kafka(conf, client_num)

    # wait loop for messages on our topic
    for message in kafka_handle:
        target = json.loads(message.value)
        db_cursor = db_connection.cursor()

        sql = """INSERT INTO {}.checks (name, host, checktime, regex_hits, regex, return_code,response_time) VALUES ('{}', '{}', to_timestamp({}) AT TIME ZONE 'UTC', {}, '{}', {}, {});""".format(
            conf.db_schema,
            target['name'],
            target['host'],
            target['checktime'],
            (target['regex_hits'] if 'regex_hits' in target else 'NULL'),
            (target['regex'] if ('regex' in target and target['regex'] != 'None') else 'NULL'),
            target['return_code'],
            target['response_time']
        )

        # prepare and commit
        db_cursor.execute(sql)
        db_connection.commit()

        m.if_debug_print("received and wrote result for {}".format(target['name']), conf)
        # TODO cleanup handles?

if __name__ == "__main__":
    main(sys.argv[1:])

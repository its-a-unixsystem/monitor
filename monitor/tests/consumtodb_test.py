#!/usr/bin/python3

import pytest


import monitor.monitorshared as m
import monitor.consumtodb as con


def test_db_connection(tmpdir):
    "test postgres connection"

    conf = m.Configuration('configx.ini', "test")

    # in case the field is empty
    if conf.db_host == '':
        pytest.skip("no broker configured in config.ini")

    db_handle = con.connect_db(conf)
    # function will fail if cannot connect
    assert db_handle

def test_kafka_connection(tmpdir):
    # we do the real config here
    conf = m.Configuration('configx.ini', "test")

    # in case the field is empty
    if conf.kafka_broker == '':
        pytest.skip("no broker configured in config.ini")

    kafka_handle = con.connect_kafka(conf, 'TESTCON')
    # function will fail if cannot connect
    assert kafka_handle


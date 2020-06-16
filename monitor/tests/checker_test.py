#!/usr/bin/python3

from pathlib import Path

import time
import pytest


import monitor.monitorshared as m
import monitor.checker as c

def createTempConfig(tmpdir, debug, targets='targets.yaml'):
    tmp_config_dir = tmpdir.mkdir("config")

    tmp_config_file = Path(tmp_config_dir / 'testconfig.ini')
    tmp_config_file.write_text("""[Application]
DEBUG = {}
Name = itsamonitor

[Kafka]
Broker = kafka:12345
SSL_CA = ca.pem
SSL_Cert = service.cert
SSL_Key = service.key
Topic = monitor_topic

[Postgres]
Host = hostname
Port = 12345
User = username
Password = secret
Schema = monitor

[Targets]
list = {}
""".format(str(debug), targets), encoding='utf-8')

def setupconf(tmpdir):
    createTempConfig(tmpdir, False, Path(tmpdir / 'targets/targets.yaml'))
    createTempTargets(tmpdir)
    return m.Configuration(str(tmpdir)+'/config/testconfig.ini', 'test')

def createTempTargets(tmpdir):
    tmp_targets_dir = tmpdir.mkdir("targets")
    tmp_targets_file = Path(tmp_targets_dir / 'targets.yaml')
    tmp_targets_file.write_text("""---
google:
    host: www.google.com
    regex: text
BBC:
    host: www.bbc.co.uk
    regex: ~
yahoo:
    host: https://news.yahoo.com/world/
    regex: ^foo.*[1]
nonexistant:
    host: test.invalid
    regex: foo
""", encoding='utf-8')


def test_target_load(tmpdir):
    "test load various targets"
    conf = setupconf(tmpdir)


    targets = []
    c.fill_targets(targets, conf)
    assert len(targets) == 4

def test_target_load_contents(tmpdir):
    "test load various targets"
    conf = setupconf(tmpdir)

    targets = []
    c.fill_targets(targets, conf)
    assert targets[0].name == 'google'
    assert targets[3].regex == 'foo'
    assert targets[2].host == 'https://news.yahoo.com/world/'

def test_host_check_valid(tmpdir):
    "test if the host check works"

    conf = setupconf(tmpdir)
    test_target = m.Targets('TESTGOOGLE', 'www.google.com', 'google')
    c.check_host(test_target, conf)
    assert test_target.return_code == 200

    # we just check if it is around %1 of the time now
    # FIXME: is that bad?
    timestamp = time.time() - time.time() * .01
    assert test_target.checktime > timestamp

    assert test_target.regex == 'google'
    assert test_target.regex_hits > 1

    # 1 second is the time-out
    assert test_target.response_time > 1 and test_target.response_time < 2*1000*1000

def test_host_check_invalid(tmpdir):
    "test if the host check works against an invalid host"

    conf = setupconf(tmpdir)
    test_target = m.Targets('TESTINVAL', 'www.invalid', '\\[[]')
    c.check_host(test_target, conf)
    assert test_target.return_code == 999

    assert test_target.response_time == 0


def test_connect_kafka(tmpdir):
    "test kafka connection"
    # we do the real config here
    conf = m.Configuration('configx.ini', "test")

    # in case the field is empty
    if conf.kafka_broker == '':
        pytest.skip("no broker configured in config.ini")

    kafka_handle = c.connect_kafka(conf)
    # function will fail if cannot connect
    assert kafka_handle

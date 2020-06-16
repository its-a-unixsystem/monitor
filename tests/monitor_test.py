#!/usr/bin/python3

from pathlib import Path


import monitor.monitorshared as m

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


def test_configuration_name(tmpdir):
    "Test the configuration functions"
    createTempConfig(tmpdir, False)
    conf = m.Configuration(str(tmpdir)+'/config/testconfig.ini', 'test')
    assert conf.myname == 'itsamonitor - test'
    assert conf.path_target_list == 'targets.yaml'

def test_configuration_targets(tmpdir):
    "Test the configuration functions"
    createTempConfig(tmpdir, False)
    conf = m.Configuration(str(tmpdir)+'/config/testconfig.ini', 'test')
    assert conf.path_target_list == 'targets.yaml'

def test_configuration_debugf(tmpdir):
    "Test the configuration functions"
    createTempConfig(tmpdir, False)
    conf = m.Configuration(str(tmpdir)+'/config/testconfig.ini', 'test')
    assert not conf.debug
    
def test_configuration_debugt(tmpdir):
    "Test the configuration functions"
    createTempConfig(tmpdir, True)
    conf = m.Configuration(str(tmpdir)+'/config/testconfig.ini', 'test')
    assert conf.debug

def test_configuration_kafka(tmpdir):
    "Test the configuration functions"
    createTempConfig(tmpdir, False)
    conf = m.Configuration(str(tmpdir)+'/config/testconfig.ini', 'test')
    assert conf.kafka_broker == 'kafka:12345'
    assert conf.kafka_SSL_CA == 'ca.pem'
    assert conf.kafka_SSL_cert == 'service.cert'
    assert conf.kafka_SSL_key == 'service.key'
    assert conf.kafka_topic == 'monitor_topic'

def test_configuration_postgres(tmpdir):
    "Test the configuration functions"
    createTempConfig(tmpdir, False)
    conf = m.Configuration(str(tmpdir)+'/config/testconfig.ini', 'test')
    assert conf.db_host == 'hostname'
    assert conf.db_port == '12345'
    assert conf.db_user == 'username'
    assert conf.db_passwd == 'secret'
    assert conf.db_schema == 'monitor'

# monitor

This monitor application monitors websites, their availability and response time and stores the data into a (Postgres) database.

It has 2 config files:
* config.ini, which needs to be located in the base directory
* targets.yaml

# requirements

1. a system to run the checks
    1. software needed: python3 with the modules psycopg2 and python3-kafka https://kafka-python.readthedocs.io, which is packaged as `python3-kafka` on Debian/Ubuntu
1. Postgres database with the schema 'monitor' and a user to access this schema.
1. running Kafka system (tested against v2.5 other might work as well)
1. anoth system for the Kafka database consumer, can be the same as 1.

# Quickstart

1. Check out the repo
1. edit both config files (config.ini and targets.yaml) as described below
1. create a topic (eg. 'monitor') on the kafka system. Depending on your expected amount of checks you might want to adjust the amount of partitions:
`bin/kafka-topics --bootstrap-server $SERVER --create --topic monitor --replication-factor 1 --partitions 2`
1. create the database schema. You can either install squitch and use the supplied squitch files via: `sqitch deploy --verify db:pg:monitor` or create the single table manually, by running:
`psql -U $USER -d monitor -a -f deploy/checks.sql"
1. start the consumer via python3 


## config.ini

This config file contains the basic configuration fo the application.

`DEBUG` : set if you want the app to produce debugging output
`Name` : the name of the application for logging and kafka consumer
`Broker/SSL_*/Topic` : the Kafka connectivity setting. *The Kafka Topic needs to exist*
`Postgres` : Postgres conncetivity setting
`Targets` : the path to the YAML file with the pages to check

```
[Application]
DEBUG = False
Name = monitor

[Kafka]
Broker = host.com:12345
SSL_CA = ca.pem
SSL_Cert = service.cert
SSL_Key = service.key
Topic = monitor

[Postgres]
Host = host.com
Port = 1234
User = username
Password = secret
Schema = monitor

[Targets]
list = targets.yaml
```

## targets.yaml

This file contains the webpages which could be checked. Each entry can also have a regex (https://docs.python.org/2/library/re.html) which is being checked on the page and the hits are being counted.

```
---
google:
    host: www.google.com
    regex: text
BBC:
    host: www.bbc.com/news
    regex: ~
yahoo:
    host: www.yahoo.com
    regex: yahoo
```

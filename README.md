# monitor

This monitor application monitors websites, their availability and response time and stores the data into a (Postgres) database.

It has 2 config files:
* config.ini, which needs to be located in the base directory
* targets.yaml

# requirements

1. a system to run the checks
    1. software needed: python3 with the modules [psycopg2](https://pypi.org/project/psycopg2/) and [python3-kafka](https://kafka-python.readthedocs.io), 
    1. The packages are available as `python3-kafka` `python3-psycopg2` on Debian/Ubuntu, you can install those packages via `sudo apt install python3-kafka python3-psycopg2`
    1. the testing needs pytest, pytest-benchmark and pytest-cov (all python 3 versions)
1. Postgres database with the schema 'monitor' and a user to access this schema. Postgres tools for setting up the table are also needed. For Debian/Ubuntu do `sudo apt install postgresql-client`
1. a running Kafka system (tested against v2.5 other versions might work as well)
1. anoth system for the Kafka database consumer, can be the same as 1.

# Quickstart

1. Check out the repo
1. edit both config files (config.ini and targets.yaml) as described below
1. create a topic (eg. 'monitor') on the kafka system. Depending on your expected amount of checks you might want to adjust the amount of partitions:
`bin/kafka-topics --bootstrap-server $SERVER --create --topic monitor --replication-factor 1 --partitions 2`
1. create the database schema. You can either install the database migration tool [squitch](sqitch.org/) and use the supplied squitch files via: `sqitch deploy` or create the table manually, by running:
`psql -U $USER -d monitor -a -f deploy/checks.sql`
1. start the consumer via `python3 consumtodb.py`
1. start on another console or system the checker via `python3 monitor.py`
1. if the checker works as expected add it to a cron-job via `crontab -e` and configure it to run at a desired interval

# Configuration

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

This file contains the webpages which could be checked. Each entry can also have a regex which is being checked on the page and the hits are being counted. It starts with three dashes and needs to be YAML conform:

```
---
NAME:
    host: HOSTNAME/PATH
    regex: SOMETHING
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
- *NAME* is a name you can give to this check, like 'blogpage' or similar, it cannot contain whitespaces, can be up to 255 characters long
- *host* the URL to the page, if it does not contain an URI like `http` or `https` then `https://` is automatically added. Can be maximum 255 characters long
- *regex* see https://docs.python.org/2/library/re.html for regex rules, if no search should be performed, you need to add a tilde (~) character instead

# Database
## format

The result table contains the following columns:
```
    name      varchar(255) NOT NULL,
    host      varchar(255) NOT NULL,
    checktime timestamp NOT NULL,
    response_time integer,
    regex_hits integer,
    regex varchar(255),
    return_code smallint
```

Table name | explanation
-----------|------------
**name** | choosen name for the check
**host** | host/path for the check
**checktime** | Postgres timestamp UTC normalized
**response time** | the response time of the page in microseconds*1000
**regex_hits** | how many times the regex was encountered on the page
**regex** | which regex was used
**return_code** | HTTP return code of that page

## check failures
If connecting to the host either times out or is unreachable, it sets the `return_code` to `999`

## DB performance limitations
there are so far two indexes on the table, on name and on checktime, as any output would filter on a date range as well as on certain checks. If different output is needed additonal indexes should be created to avoid table scans.

# known limitations

 Issue | Mitigation
-------|-----------
it is vulnerable to Kafka connection issues and will just exit|wrap it in a environment, that does restart it, eg. crontab for the checker and supervia/systemd for the consumer
it is limited to one database|with indexes output should be sufficent fast, but app can not scale further
the checker works serial and is too slow on many checks|start more than one with different targets.yaml
I need to start mroe than one DB consumer| start the application several times with a different parameter `-i <number>`
I need to have several instances with different configurations| you can use the parameter `-c <configuration-file.ini>`
I need to check a site that need authentication/cookies/etc| not implemented, sorry
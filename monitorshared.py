"shared functions for the monitor"
import configparser
import os
import sys

# "data structure" for a single target check
class Targets(object):
    "target list"
    regex_hits = 0
    response_time = None
    return_code = None

# idea from https://www.daniweb.com/programming/software-development/code/216631/a-list-of-class-objects-python
    def __init__(self,
                 name=None,
                 host=None,
                 regex=None,
                 checktime=0):
        self.name = name
        self.regex = regex
        self.host = host
        self.checktime = checktime


# maintains the configuration of the app
class Configuration(object):
    "maintain the app config"
    debug = 0
    myname = os.path.basename(__file__)
    target_file_path = "NOTSET"
    path_target_list = "NOTSET"

    def __init__(self, config_file_path, name="DEFAULT"):

        self.config_file_path = config_file_path

        if config_file_path == '':
            config_file_path = 'config.ini'

        # open the config
        # TODO make the file a command line option
        config = configparser.ConfigParser()

        try:
            config.read_file(open(config_file_path))
        except:
            error_print("cant open " + config_file_path)
            sys.exit(1)

        # set my name to $NAME - checker/consumer
        self.myname = config.get('Application',
                                 'Name',
                                 fallback=os.path.basename(__file__))
        self.myname = self.myname + " - " + name


        # set the Kafka connectivity params
        self.kafka_broker = config.get('Kafka',
                                       'Broker')
        self.kafka_SSL_CA = config.get('Kafka',
                                       'SSL_CA')
        self.kafka_SSL_cert = config.get('Kafka',
                                         'SSL_Cert')
        self.kafka_SSL_key = config.get('Kafka',
                                        'SSL_Key')
        self.kafka_topic = config.get('Kafka',
                                      'Topic')

        # set the database configuration
        self.db_host = config.get('Postgres',
                                  'Host')
        self.db_port = config.get('Postgres',
                                  'Port')
        self.db_user = config.get('Postgres',
                                  'User')
        self.db_schema = config.get('Postgres',
                                    'Schema')
        # TODO - not safe, needs secrets management
        self.db_passwd = config.get('Postgres',
                                    'Password')

        # set debug var
        self.debug = config.getboolean('Application', 'DEBUG', fallback=False)
        if_debug_print("debug mode enabled", self)

        # set the path to the target YAML file
        # we ignore if the value is not set, trying to open it will catch it
        self.path_target_list = config.get('Targets', 'list')


def error_print(message, conf=None):
    "print a error log line"

    if conf is not None:
        sys.stderr.write(conf.myname + ": " + message + "\n")
    else:
        sys.stderr.write(os.path.basename(__file__) + ": " + message + "\n")

def if_debug_print(message, conf):
    "print message if we are in debug mode"
    if not conf.debug:
        return
    error_print(message, conf)

import json
import os
import logging


class Config:
    __instance = None
    LOGFILENAME = 'lion.log'

    @classmethod
    def get_instance(cls):
        """ Static access method. """
        if Config.__instance is None:
            Config()
        return Config.__instance

    @classmethod
    def get_level(cls, logLevel):
        if logLevel == "debug":
            return logging.DEBUG
        elif logLevel == "info":
            return logging.INFO
        elif logLevel == "warning":
            return logging.WARNING
        elif logLevel == "error":
            return logging.ERROR
        elif logLevel == "critical":
            return logging.CRITICAL
        else:
            return logging.DEBUG

    def __init__(self):
        """ Virtually private constructor. """
        if Config.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open("".join([dir_path, os.path.sep, "config.json"])) as json_file:
                data = json.load(json_file)
            env = data["Env"]
            Config.__instance = data[env]

            logLevel = data[env]['Site']['LogLevel']
            if data[env]['Site']['LogToFile']:
                logging.basicConfig(filename=Config.LOGFILENAME, format='%(asctime)s %(levelname)s - %(message)s', level=Config.get_level(logLevel))
            else:
                logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=Config.get_level(logLevel))

import mysql.connector
from mysql.connector import pooling

class Db:
	__instance = None
	
	@classmethod
	def get_connection(cls):
		""" Static access method. """
		if Db.__instance is not None:
			return Db.__instance.get_connection()
	
	@classmethod
	def get_instance(cls, config):
		""" Static access method. """
		if Db.__instance == None:
			Db(config)
		return Db.__instance

	def __init__(self, config):
		""" Virtually private constructor. """		
		if Db.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			dbconfig = {
				"host" : config['Database']['Host'],
				"port" : config['Database']['Port'],
				"database" : config['Database']['Name'],
				"user" : config['Database']['Username'],
				"password" : config['Database']['Password']
			}

			Db.__instance = pooling.MySQLConnectionPool(pool_name = config['Site']['Name'], pool_size = config['Database']['PoolSize'], **dbconfig)
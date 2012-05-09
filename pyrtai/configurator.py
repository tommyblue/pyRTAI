## @package pyrtai
# This package handles the configurations

import ConfigParser
import os

from pyrtai.custom_exceptions import RtaiConfigError

## Configurator class handles config values. 
#
# The default action is to check if the value exists then return it or
# return the value parsed from the config file otherwise.
# The default file is defaults.cfg but a different one can be passed
# as parameter to the constructor.
class Configurator:
	## @var config
	# The ConfigParser instance
	
	## @var protocol
	# The protocol to use to connect to the server (HTTP/HTTPS)
	
	## @var address
	# The address to connect to
	
	## @var port
	# The port to connect to
	
	## @var target_name
	# The name of the target server
	
	## @var host
	# The host to connect to. It can be built using PROTOCOL://ADDRESS:PORT
	
	## @var session_id
	# The session name
	
	## @var is_slave_connection
	# Booblean value which indicates if it's a slave connection. It's a master collection if False
	
	## @var slave_port
	# The port to be used to connect to slave server
	
	## @var slave_data_port
	# The port to be used to connect to slave data stream
	
	## The constructor reads the config file, which can be passed as param. Raises a RtaiConfigError if the file can't be found.
	# @param config_file The path to the config file. If not specified is used defaults.cfg in the script directory
	def __init__(self, config_file = None):
		self.config = ConfigParser.ConfigParser()
		
		# Initializes member vars
		self.protocol = None
		self.address = None
		self.port = None
		self.host = None
		self.session_id = None
		self.slave_port = None
		self.slave_data_port = None
		self.target_name = None
		self.is_slave_connection = False
		
		if config_file is None:
			config_file = os.path.dirname(__file__) + '/defaults.cfg'
		
		try:
			self.config.read(config_file)
		except NameError:
			raise RtaiConfigError(config_file, 'Error while reading config file')

	## Sets member vars
	# @param key The name of the var
	# @param value The value to assign to the var
	# @return The value of the assigned var
	
	def setAttr(self, key, value):
		self.__dict__[key] = value
		return self.__dict__[key]
	
	## Gets member vars from __dict__ or from the config file if not previously assigned
	# @param key The name of the member var to retrieve
	# @return The value of the var. None if not present in the __dict__ or in the config file
	def getAttr(self, key):
		try:
			if self.__dict__[key] is not None:
				return self.__dict__[key]
			else:
				try:
					return self.setAttr(key, self.config.get('Server', key))
				except NameError:
					return None
		except KeyError:
			try:
				return self.setAttr(key, self.config.get('Server', key))
			except NameError:
				return None
	
	## Get the full Url to connect to
	# @return Returns the address of the target server, e.g. http://192.168.1.1:29500
	def getUrl(self):
		return "%s://%s:%s" % (self.getAttr('protocol'), self.getAttr('address'), self.getAttr('port'))
		
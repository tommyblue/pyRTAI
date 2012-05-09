## @package pyrtai
# Represents the target server (master or slave)
# @see pyrtai::target::Target
# TODO: Gestire lo stato del target

from connector import Connector
from configurator import Configurator
from data_poller import DataPoller
from data_collector import DataCollector

class Target:
	## @var config
	# A configurator::Configurator object
	
	## @var connection
	# A connector::Connector instance used to send commands to XML-RPC connection
	
	## @var is_slave
	# Shows if this is a slave target
	
	## @var parameters
	# The target parameters
	
	## @var datastream_queue
	# The queue where DataCollector thread puts data and observers get it
	
	## @var datastream_poller
	# The DataPoller thread
	
	## @var datastream_collector
	# The DataCollector thread
	
	## @var is_connected
	# Checks if the Target is connected or not. Actually the status is simply set bu connect() and disconnect()
	
	## Target initializer.
	def __init__(self, slave = False, protocol = None, address = None, port = None, target_name = None):
		self.config = Configurator()
		self.is_connected = False
		self.is_slave = slave
		self.parameters = None
		self.datastream_queue = None
		self.datastream_poller = None
		self.datastream_collector = None
		
		# Sets basic configurations
		if protocol:
			self.config.setAttr('protocol', protocol)
			
		if address:
			self.config.setAttr('address', address)
		
		if port:
			self.config.setAttr('port', port)

		if target_name:
			self.config.setAttr('target_name', target_name)
			
		# Initializes connection
		self.connection = Connector(self.config)
	
	## Prints a summary of the target and its status
	# TODO: Decidere che informazioni restituire
	def getInfo(self):
		print "Target name: %s" % self.config.getAttr('target_name')
		print "Connection status: %s" % ("Connected" if self.is_connected else "Disconnected")
		print "Connection request: %s://%s:%s" % (self.config.getAttr('protocol'), self.config.getAttr('address'), self.config.getAttr('port'))
	
	## Setups the queue and the threads needed to read the data stream
	# @param sample_time The sample time of the signal
	# @param decimation The decimation to use
	# @return The boolean result of the operation
	def setup_data_threads(self, sample_time, decimation = None):
		if self.is_slave:
			if not self.datastream_queue:
				#self.datastream_queue = Queue()
				self.datastream_queue = []
			
			# TODO: creare un DataPoller per ogni segnale (non per tutta la traccia) e registrare gli observer sugli specifici DataPoller. 
			if not self.datastream_poller:
				self.datastream_poller = DataPoller(self.datastream_queue, sample_time, decimation)
				self.datastream_poller.start()
				
			# TODO: Il DataCollector deve leggere il numero di segnale e usare la coda specifica per inserirci i dati
			if not self.datastream_collector:
				# TODO: Fermare i thread alla chiusura del target
				self.datastream_collector = DataCollector(self.config.getAttr('address'), self.config.getAttr('slave_data_port'), self.datastream_queue)
				self.datastream_collector.start()
				
			return True
		else:
			print("Can't setup the data stream threads on a not-slave server")
			return False
	
	## Stops the data threads
	# @return The boolean result of the operation
	def stop_data_threads(self):
		if self.is_slave:
			
			if self.datastream_collector:
				print("Shutting down DataCollector thread")
				self.datastream_collector.stop()
				self.datastream_collector.join(15.0)
				if self.datastream_collector.is_alive():
					print("Can't stop the DataCollector thread, timeout occurs")
				else:
					print("DataCollector thread was shut down")
					
			if self.datastream_poller:
				print("Shutting down DataPoller thread")
				self.datastream_poller.stop()
				self.datastream_poller.join(15.0)
				if self.datastream_poller.is_alive():
					print("Can't stop the DataPoller thread, timeout occurs")
				else:
					print("DataPoller thread was shut down")
			
			# Clears vars
			self.datastream_poller = None
			self.datastream_collector = None
			self.datastream_queue = None
				
			return True
		else:
			print("Can't stop the data stream threads on a not-slave server")
			return False
		
	## Add a new observer "update" method to the list of observers.
	# @param update_method Is the method of the observer which will be called when new data arrives. The method name is arbitrary, but it must accept a string parameter
	# @param channel The optional channel to register the observer to
	# @param sample_time The sample time of the signal
	# @param decimation The decimation to use
	# @return The ID of the observer, to be used to remove the observer
	def addObserver(self, update_method, sample_time, decimation = None, channel = None):
		self.setup_data_threads(sample_time, decimation)
		return self.datastream_poller.addObserver(update_method, channel)
	
	## Removes the observer
	# @param observer_id The ID of the observer to remove
	# @return False if the observer isn't in the observers list, True if it was correctly removed
	def removeObserver(self, observer_id):
		return self.datastream_poller.removeObserver(observer_id)
			
	## Connect to the target server. Checks if master or server and call the right method on connector::Connector
	# @param password The (optional) password to catch a running master connection
	# @return The boolean result of the operation
	def connect(self, password = None):
		if self.is_slave:
			if self.connection.connectSlave(): #TODO: Cambiare il metodo di connessione non passando tutto il Configurator ma usando i dati passati nel costruttore di Connector
				self.is_connected = True
				return True
			else:
				return False
		else:
			result = self.connection.Connection_Request(password) # Passing self.config to let the Connector set some connection data (e.g. the session_id)
			self.is_connected = result
			return result
	
	## Checks if master and if affirmative, returns the slave
	# @param target_name The target to connect to. If None gets the name from the default configuration
	# @return The slave Target or False if not a master target
	def getSlave(self, target_name = None):
		if self.is_slave:
			print "Can't ask for a slave to a slave. Try asking to a master."
			return False
		else:	
			# If target is not specified, caller are requesting a "standard" connection to the primary slave target
			if not target_name:
				target_name = self.config.getAttr('target_name')
			
			slave = Target(True, self.config.getAttr('protocol'), self.config.getAttr('address'), self.config.getAttr('slave_port'), target_name)
			# Sets the session ID
			slave.config.setAttr('session_id', self.config.session_id)
			return slave
		
	## Disconnects from the XML-RPC server
	# @return The boolean result of the operation
	def disconnect(self):
		if self.is_slave:
			result = self.connection.disconnect()
			self.is_connected = result
			return result
		else:
			print("Can't call disconnect on master server")
			return False
	
	## Stops target server. This method, called on a master server, calls connector::Connector::stopServer and called on slave, calls connector::Connection::stopSlave
	# @return The boolean result of the operation
	def stop(self):
		if self.is_slave:
			# TODO: Stop the data thread if active
			result = self.connection.stopSlaveServer()
			self.is_connected = result
			# Stops data threads
			self.stop_data_threads()
			return result
		else:
			result = self.connection.stopMasterServer()
			self.is_connected = result
			return result
	
	## Closes the session
	# @return The boolean result of the operation
	def close(self):
		result = self.connection.closeSession()
		# Stops data threads
		self.stop_data_threads()
		self.is_connected = result
		return result
	
	## Stops the target
	# This method closes the data threads (if they exist) then closes the session
	# @return The boolean result of the operation
	def halt(self):
		self.stop_data_threads()
		result = self.connection.stopTarget()
		self.is_connected = result
		return result
	
	## Starts the connected target
	# @return The boolean result of the operation
	def start(self):
		return self.connection.start()
	
	## Starts data transfer for the specified signal
	# @param signal_number The number of the signal to start
	# @param sample_time The sample time of the signal
	# @param decimation The decimation to use
	# @return The boolean result of the operation 
	def startData(self, signal_number, sample_time, decimation = None):
		self.setup_data_threads(sample_time, decimation)
		return self.connection.startData(signal_number, decimation)
	
	## Stops (all) data transfers
	# @param signal_number The number of signal to catch
	# @param all_data If True calls StopAllData(). Calls StopData() if False.
	# @return The boolean result of the operation
	def stopData(self, signal_number = None, all_data = False):
		# TODO: Devo chiudere anche i threads dei poller?
		if all_data:
			return self.connection.stopAllData()
		elif signal_number:
			return self.connection.stopData(signal_number)
		else:
			print("Can't stop data without signal number or all_data flag")
			return False
	
	## Get the structure of the signals
	# @return The structure of the signals or False if the target has no signals
	def getSignalStructure(self):
		return self.connection.getSignalStructure()
	
	## Sends new parameters to the server
	# @param params The array of parameters to set
	# @return The boolean result of the operation
	def setParameters(self, params):
		return self.connection.setParameters(params)
	
	## Get the parameters from the target server
	# @return An array of params. Every param is an hash
	def getParameters(self):
		self.parameters = self.connection.getParameters()
		return self.parameters
	
	## Interface to set a single param
	# @param identifier The identifier string to get the param to update
	# @param value The value to set to the param
	def setParam(self, identifier, value):
		if not self.parameters:
			self.parameters = self.connection.getParameters()
		ids = identifier.split("/")
		param_name = ids.pop()
		block_name = "/".join(ids)
		new_params = []
		for param in self.parameters:
			if param['block_name'] == block_name and param['param_name'] == param_name:
				param['values'] = value
			new_params.append(param)
		self.parameters = new_params
		return self.setParameters(self.parameters)
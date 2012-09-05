## @package pyrtai
# Handles the connection to the RTAI server
# @see pyrtai::connector::Connector

import socket
import time
from xmlrpclib import ServerProxy, Fault
from utility import getStateFromResponse
## The Connector class connect to the RTAI server and manage responses
# and basic operations on it
class Connector:
    ## @var connection
    # xmlrpclib::ServerProxy connection to XML-RPC server

    ## The constructor instantiates the configurator::Configurator object
    # @param config The configurator::Configurator object, shared with the Target
    def __init__(self, config):
        # Set some member var
        self.connection = None
        self.config = config

    ## Connect to the target server and handles the response to extract the slave server data params. The data is saved in the configurator::Configurator object passed as first param.
    # @param password The (optional) password to catch a running master connection
    # @return The boolean result of the operation
    def Connection_Request(self, password = None):
        try:
            self.connection = ServerProxy(self.config.getUrl())
            print("Connecting to %s" % self.config.getUrl())
            if password:
                req = self.connection.Connection_Request(self.config.getAttr('target_name'), password)
            else:
                req = self.connection.Connection_Request(self.config.getAttr('target_name'))
            if req['state'] == 0:
                self.config.setAttr('session_id', req['id_session'])
                self.config.setAttr('slave_port', req['port'])
                return True
            else:
                return False
        except socket.error:
            print('Error connecting to the server, check network')
            return False

    ## Connect to Slave server
    # @return The boolean result of the operation
    def connectSlave(self):
        try:
            print("Connecting to slave at %s with session ID %s" % (self.config.getUrl(), self.config.getAttr('session_id')))
            print("Waiting 5 seconds to let the target start...")
            time.sleep(5)
            self.connection = ServerProxy(self.config.getUrl())
            req = self.connection.tConnect(self.config.getAttr('session_id'))
            state = getStateFromResponse(req['state'])
            if not state['error']:
                self.config.setAttr('slave_data_port', req['port'])
                print("Slave connected with result %s. Data port %s opened" % (req['str'], req['port']))
                return True
            else:
                return False
        except Exception, e:
            print e
            return False

    ## Disconnect from the server
    # @return The boolean result of the operation
    def disconnect(self):
        try:
            req = self.connection.Disconnect(self.config.getAttr('session_id'))
            state = getStateFromResponse(req['state'])
            if not state['error']:
                print("Server successfully disconnected with result %s" % req['str'])
                return True
            else:
                return False
        except:
            return False

    ## Detach the session
    # @return The boolean result of the operation
    def closeSession(self):
        try:
            response = self.connection.Close_Session(self.config.getAttr('target_name'), self.config.getAttr('session_id'))
            if response["state"] == 0:
                print "Success with message: \"%s\"" % (response['str'])
                return True
            else:
                print "Error with message: \"%s\"" % (response['str'])
                return False
        except socket.error, v:
            print('Error connecting to the server, check network')
            return False

        except Fault, v:
            print "Failure detected with code %s and message \"%s\"" % (v.faultCode, v.faultString)
            return False
        except:
            print('Error while reading config file')
            return False

    ## Stops master server
    # @return The boolean result of the operation
    def stopMasterServer(self):
        try:
            response = self.connection.Stop_Master_Server(self.config.getAttr('target_name'))
            if response["state"] == 0:
                print "Success with message: \"%s\"" % (response['str'])
                return True
            else:
                print "Error with message: \"%s\"" % (response['str'])
                return False
        except socket.error, v:
            print('Error connecting to the server, check network')
            return False

        except Fault, v:
            print "Failure detected with code %s and message \"%s\"" % (v.faultCode, v.faultString)
            return False
        except:
            print('Error while stopping the server')
            return False

    ## Stops slave server
    # @return The boolean result of the operation
    def stopSlaveServer(self):
        try:
            response = self.connection.Stop_Server(self.config.getAttr('session_id'))
            if response["state"] == 0:
                print "Success with message: \"%s\"" % (response['str'])
                return True
            else:
                print "Error with message: \"%s\"" % (response['str'])
                return False
        except socket.error, v:
            print('Error connecting to the server, check network')
            return False

        except Fault, v:
            print "Failure detected with code %s and message \"%s\"" % (v.faultCode, v.faultString)
            return False
        except:
            print('Error while stopping the server')
            return False

    ## Calls Info_RT on the server	
    # @return The boolean result of the operation
    def getInfo(self):
        try:
            response = self.connection.Info_RT(self.config.getTargetName())

            if response["state"] == 0:
                print "Success with message: \"%s\"" % (response['str'])
                return True
            else:
                print "Error with message: \"%s\"" % (response['str'])
                return False
        except socket.error, v:
            print('Error connecting to the server, check network')
            return False

        except Fault, v:
            print "Failure detected with code %s and message \"%s\"" % (v.faultCode, v.faultString)
            return False
        except:
            print('Error while reading config file')
            return False

    ## Stops the target
    # @return The boolean result of the operation
    def stopTarget(self):
        try:
            req = self.connection.Stop(self.config.getAttr('session_id'))
            # TODO: in case of error the response is {'state': 0, 'str': 'No TEST target or bad interface task identifier'} and not in the 4-bit format!
            state = getStateFromResponse(req['state'])
            if not state['error']:
                print("Server successfully stopped with result %s" % req['str'])
                return True
            else:
                return False
        except:
            return False

    ## Starts the target
    # @return The boolean result of the operation
    def start(self):
        try:
            req = self.connection.Start(self.config.getAttr('session_id'))
            state = getStateFromResponse(req['state'])
            if not state['error']:
                print("Server successfully started with result %s" % req['str'])
                return True
            else:
                return False
        except:
            return False

    ## Asks the parameters to the XML-RPC server
    # @return Returns False if an error occurred. Otherwise returns an array of parameters. Each parameter is an hash with 5 elements: block_name, param_name, rows, cols, values. Values is a matrix of rows*cols elements.
    def getParameters(self):
        parameters = []
        try:
            response = self.connection.Get_Param(self.config.getAttr('session_id'))
            if len(response) <= 1:
                if response["state"] == 0:
                    print "Success response state but with unespected results. Message: \"%s\"" % (response['str'])
                    return False
                else:
                    print "Error with message: \"%s\"" % (response['str'])
                    return False
            else:
                msg = response.pop(0)
                state = getStateFromResponse(msg['state'])
                if state['error']:
                    print "Error with message: \"%s\"" % (msg['str'])
                    return False
                else:
                    for val in response:
                        struct = {}
                        struct['block_name'] = val[0]
                        struct['param_name'] = val[1]
                        struct['rows'] = val[2]
                        struct['cols'] = val[3]
                        struct['values'] = val[4]
                        parameters.append(struct)
                    return parameters
        except:
            return False

    ## Sets the parameters into the target.
    # @param params The full set of params to send to the server
    # @return The boolean result of the operation
    def setParameters(self, params):
        values = [self.config.getAttr('session_id')]

        formatted_params = []
        for val in params:
            element = []
            element.append(val['block_name'])
            element.append(val['param_name'])
            element.append(val['rows'])
            element.append(val['cols'])
            element.append(val['values'])
            formatted_params.append(element)

        values.append(formatted_params)
        try:
            response = self.connection.Send_Param(values)
            # TODO: Fare il check controllando l'esistenza della chiave 'state' e non sulla lunghezza
            if len(response) <= 2:
                if response["state"] == 0:
                    print "Success response state but with unespected results. Message: \"%s\"" % (response['str'])
                    return False
                else:
                    print "Error with message: \"%s\"" % (response['str'])
                    return False
            else:
                msg = response.pop(0)
                state = getStateFromResponse(msg['state'])
                if state['error']:
                    print "Error with message: \"%s\"" % (msg['str'])
                    return False
                else:
                    return response
        except:
            return False

    ## Starts data transfer for the specified signal
    # @param signal_number The number of the signal to start
    # @param decimation The decimation to use (optional)
    # @return The boolean result of the operation 
    # TODO: startData deve anche segnalare a DataCollector di partire (impostando un flag), altrimenti DataCollector rimane in attesa
    def startData(self, signal_number, decimation = False):
        try:
            if decimation:
                req = self.connection.Start_Data(self.config.getAttr('session_id'), signal_number, decimation)
            else:
                req = self.connection.Start_Data(self.config.getAttr('session_id'), signal_number)
            state = getStateFromResponse(req['state'])
            if not state['error']:
                print("Data successfully started for signal %d with result %s" % (signal_number, req['str']))
                return True
            else:
                return False
        except:
            return False

    ## Stops data transfer from a specified signal
    # @param signal_number The number of the signal to stop
    # @return The boolean result of the operation
    def stopData(self, signal_number):
        try:
            req = self.connection.Stop_Data(self.config.getAttr('session_id'), signal_number)
            state = getStateFromResponse(req['state'])
            if not state['error']:
                print("Data successfully stopped for signal %d with result %s" % (signal_number, req['str']))
                return True
            else:
                return False
        except:
            return False


    ## Stops all the data transfers
    # @return The boolean result of the operation
    def stopAllData(self):
        try:
            req = self.connection.Stop_All_Data(self.config.getAttr('session_id'))
            state = getStateFromResponse(req['state'])
            if not state['error']:
                print("Data successfully stopped with result %s" % req['str'])
                return True
            else:
                return False
        except:
            return False

    ## Get the structure of the signals
    # @return Returns False if an error occurred or the target has no signals. Otherwise returns an array of signals. Every signal is an hash with 5 elements: number (int), name (string), traces_num (int), sample_time (double), traces_names (array).
    def getSignalStructure(self):
        structure = []
        try:
            response = self.connection.Get_Signal_Structure(self.config.getAttr('session_id'))
            if len(response) <= 1:
                if response["state"] == 0:
                    print "Success response state but with unespected results. Message: \"%s\"" % (response['str'])
                    return False
                else:
                    print "Error with message: \"%s\"" % (response['str'])
                    return False
            else:
                msg = response.pop(0)
                state = getStateFromResponse(msg['state'])
                if state['error']:
                    print "Error with message: \"%s\"" % (msg['str'])
                    return False
                else:
                    for index, val in enumerate(response):
                        struct = {}
                        # Gets the index which will be used to call other methods which wants the number of the signal
                        struct['number'] = index
                        struct['name'] = val['str']
                        struct['traces_num'] = val['i4']
                        struct['sample_time'] = val['d']
                        struct['traces_names'] = val['tstr']

                        # If 'traces_names' creates problems we can use:
                        #for k, v in val.iteritems():
                            #struct[k] = v

                        structure.append(struct)
                    return structure
        except:
            return False

    ## Debug method to call functions directly to RPC connection
    # @param function_name The name of the method to call
    # @param params The params to pass to the method above
    # @return The response of the call	
    def callMethod(self, function_name, params):
        return getattr(self.connection, function_name)(*params)


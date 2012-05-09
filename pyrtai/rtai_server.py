## @package pyrtai
# Represents the target server (master or slave)
# @see pyrtai::rtai_server::RtaiServer

from target import Target

class RtaiServer:
    ## @var master
    # The master RTAI-XML server
    
    ## @var slave
    # The slave RTAI-XML server
    
    ## @var protocol
    # The protocol to use to connect to the server (http|https)
    
    ## @var address
    # The address of the server
    
    ## @var port
    # The port to use on the server
    
    ## @var target_name
    # The target name to connect to
    
    ## RtaiServer initializer. If the params are None, they're extracted from self.configurator
    # when the Target is created
    # @param target_name The target name to connect to (TODO: e' lo script name, non il targe name)
    # @param protocol The protocol to use to connect to the server (http|https)
    # @param address The address of the server
    # @param port The port to use on the server
    def __init__(self, target_name = None, protocol = None, address = None, port = None):
        self.master = None
        self.slave = None
        self.protocol = protocol
        self.address = address
        self.port = port
        self.target_name = target_name
    
    ## Creates the target
    # If the first connection, it connects to master, then to the slave.
    # If a slave_target param is passed, it connects to the specified target
    # @param target_name The target to connect to. Can be None to request a standard slave target
    # @param password The master password to catch a running server
    # @return The connected target. False if an error occurs (the error message is printed)
    def getTarget(self, target_name = None, password = None):
        # Override self.target_name if set
        if not target_name:
            target_name = self.target_name
            
        # TODO: Controllare anche che il master sia connesso. Se e' configurato ma non connesso si deve solo connettere. Il problema e' che non c'e' modo di sapere se effettivamente e' connesso
        if not self.master:
            print("Connecting to master")
            # The first parameter as False creates a Master target
            self.master = Target(False, self.protocol, self.address, self.port, target_name)
        
        # TODO: Serve lo stato del master per capire se e' gia' connesso (e quindi ci si riconnette) oppure se serve una nuova connessione
        if self.master.is_connected or self.master.connect(password):
            print("Connected to master")
        else:
            print("Error while connecting to master")
            return False
        
        print("Connecting to slave")

        self.slave = self.master.getSlave(target_name)
    
        if self.slave and (not self.slave.is_connected) and self.slave.connect():
            print("Connected to slave")
        else:
            print("Error while connecting to the slave target")
    
        return self.slave
        
    ## Stops everything
    def halt(self):
        self.slave.halt()
        #self.master.halt() # TODO: Va chiamato anche sul master?
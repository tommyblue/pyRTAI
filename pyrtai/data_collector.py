# @package data_collector
# Handles the data connection with XML-RPC server

from threading import Thread
import socket

# TODO: Il collector deve stare fermo finche' non viene dato il via ad almeno un segnale 
class DataCollector(Thread):
    ## @var socket
    # The socket where the signals are read

    ## @var queue
    # The datastream queue

    ## @var done
    # Flag to stop the thread

    ## Initializes the object setting the queue and the thread
    def __init__(self, address, port, queue):
        self.queue = queue
        Thread.__init__(self)
        self.name = 'DataCollector'
        #self.socket = socket.create_connection( (address, port) )
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Setto 1 secondo di timeout per evitare che rimanga appeso quando il server
        # smette di servire dati
        self.socket.settimeout(1.0)
        self.socket.connect( (address, port) )

    ## Stops thread
    def stop(self):
        self.done = True

    ## A beta method to split the socket into lines
    def run(self):
        line_buffer = self.socket.recv(4096)
        self.done = False

        # Reads from the socket until the 'endSocket' line
        while not self.done:
            #print line_buffer
            if '\n' in line_buffer:
                splitted = line_buffer.split('\n')
                for i in range(len(splitted)):
                    line = splitted[i]
                    # If last element splitted, restart the cycle
                    if i == (len(splitted)-1):
                        # TODO: Capire come viene generato 'endSocket' e se questo check su linke_buffer funziona
                        # Ad esempio si potrebbe usare il check line.sptrip() == 'endSocket' ma bisogna accertarsi che non ci siano \n o \r
                        if 'endSocket' in line:
                            print "endSocket detected, stopping the collector thread"
                            self.done = True
                        else:
                            #print "Cycle end (%d), adding %s from %s to next line" % (i, line, splitted,)
                            line_buffer = line
                    # Elsewhise the line is good
                else:
                    #print "[%d] => %s (%d)" % (i, line, len(splitted))
                        self.queue.insert(0, line)
            else:
                # Intercetto il timeout
                try:
                    line_buffer = line_buffer + self.socket.recv(4096)
                except:
                    #pass
                    raise

        # Closes the socket		
        self.socket.shutdown(1)
        self.socket.close()

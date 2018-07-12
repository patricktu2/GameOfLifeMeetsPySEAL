'''
@Author: Patrick Tu & Kathrin Witzlsperger

'''

import threading
import time
from seal import Evaluator, Ciphertext

class Threaded_server(threading.Thread):
    '''
    This class simulates a server as a thread. The thread waits for a incoming message in
    the queue from client, computes the state of the new grid encryptedly and sends
    the new encrypted grid to the client by another queue
    '''

    def __init__(self, N, server_to_client_queue, client_to_server_queue, encryptionContext ):

        self.N = N #assign gridsize
        self.client_to_server_queue = client_to_server_queue # create the queue
        self.server_to_client_queue = server_to_client_queue
        self.encryptionContext = encryptionContext # type: SEALContext(parms)
        self.running = 1
        #delay for the periodic calls
        self.delay =0.001
        threading.Thread.__init__(self)

    def run(self):
        '''
        Start threads and calls periodic Calls
        :return:
        '''

        print("[SERVER SIMULATION] Threaded Server Run")
        self.periodicCall()

    def periodicCall(self):
        '''
        Checks every 1 ms if a message is in the queue.
        If a messafe is in the queue process it.
        :return:
        '''

        print("[SERVER SIMULATION] Start periodic call")
        while self.running:
            if self.client_to_server_queue.qsize():
                print("[SERVER SIMULATION] Simulated Thread Server running")
                self.processMessage()
            else:
                #print("[SERVER] Server thread sleeps 1 ms")
                time.sleep(self.delay)


    def processMessage(self):
        '''
        Fetches a message from the queue and computes encrypted operations to get the generation / new grid state
        and pushes new encrypted grid state in the queue to the client
        :return:
        '''

        print("[SERVER SIMULATION] Start fetching message")
        # fetch Message from queue, message is a dictionary with structure
        # {"encrypted_old_grid": encrypted_old_grid, "encrypted_live_neighbours_grid": encrypted_live_neighbours_grid}
        message_from_client = self.client_to_server_queue.get(0)
        print("[SERVER SIMULATION] In Queue", message_from_client)
        encrypted_old_grid = message_from_client["encrypted_old_grid"]
        encrypted_live_neighbours_grid = message_from_client["encrypted_live_neighbours_grid"]

        # Pyseal Evaluator
        evaluator = Evaluator(self.encryptionContext)

        # Computation of new grid
        encrypted_new_grid = []
        for i in range(self.N * self.N):
            encrypted_result = Ciphertext()
            evaluator.add(encrypted_old_grid[i], encrypted_live_neighbours_grid[i], encrypted_result)
            encrypted_new_grid.append(encrypted_result)

        print("[SERVER SIMULATION] New Grid Computed")
        print("[SERVER SIMULATION] Message to client ", encrypted_new_grid)
        self.server_to_client_queue.put(encrypted_new_grid)
        print("[SERVER SIMULATION] Put computed grid into server to client queue")



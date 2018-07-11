'''
@Author: Patrick Tu

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
        #assign gridsize
        self.N = N
        # create the queue
        self.client_to_server_queue = client_to_server_queue
        self.server_to_client_queue = server_to_client_queue
        self.encryptionContext = encryptionContext # type: SEALContext(parms)
        self.running = 1
        #delay for the periodic calls
        self.delay =0.2
        threading.Thread.__init__(self)

    def run(self):
        '''
        Start threads and calls periodic Calls
        :return:
        '''
        print("[SERVER] Threaded Server Run")
        self.periodicCall()

    def periodicCall(self):
        '''
        Checks every 200ms if a message is in the queue.
        If a mesasge is in the queue process it.
        :return:
        '''
        print("Start periodic call")
        while self.running:
            if self.client_to_server_queue.qsize():
                print("[SERVER]running")
                self.processMessage()
            else:
                print("[SERVER] Server thread sleep 200ms")
                time.sleep(self.delay)


    def processMessage(self):
        '''
        Fetches a message from the queue and computes encrypted operations to get the generation / new grid state
        and pushes new encrypted grid state in the queue to the client
        :return:
        '''
        print("[SERVER] Start fetching message")
        # fetch Message from queue, message is a dictionary with structure
        # {"encrypted_old_grid": encrypted_old_grid, "encrypted_live_neighbours_grid": encrypted_live_neighbours_grid}
        message_from_client = self.client_to_server_queue.get(0)
        print("[SERVER] In Queue", message_from_client)
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

        print("[SERVER] New Grid Computed")
        print("[SERVER] Message to client ", encrypted_new_grid)
        self.server_to_client_queue.put(encrypted_new_grid)
        print("[SERVER] Put computed grid into server to client queue")



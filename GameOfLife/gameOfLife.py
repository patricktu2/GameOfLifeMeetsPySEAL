#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Patrick Tu & Kathrin Witzlsperger
"""

import numpy as np
import random
import encryption
import time
import socket
from io import BytesIO
import sys
from GameOfLife.helper import Helper


class GameOfLife:
    '''
    This class models Conways Game of Life as a simple squared NxN grid, where each cell in the grid
    can have the values 1 (alive) or 0 (dead). Furthermore, an instance method updates the generation
    t of the grid to generation t+1.
    '''

    def __init__(self, N):
        """
        Set up Conway's Game of Life and initialize a random configuration of dead and alive
        cells on the board.
        """

        # dimension of grid (N*N = number of cells)
        self.N = N
        # matrix representing old generation
        self.old_grid = np.zeros(N * N, dtype='i').reshape(N, N)
        # matrix representing new generation
        self.new_grid = np.zeros(N * N, dtype='i').reshape(N, N)
        # matrix to store live neighbours of each cell
        self.live_neighbours_grid = np.zeros(N * N, dtype='i').reshape(N, N)

        # set up a random initial configuration for the grid
        # each point is either alive or dead, represented by integer values of 1 and 0, respectively
        for i in range(0, self.N):
            for j in range(0, self.N):
                if (random.randint(0, 100) < 15):
                    self.old_grid[i][j] = 1
                else:
                    self.old_grid[i][j] = 0

        # initialize encryption
        self.encryption = encryption.Encryption()


    def live_neighbours(self):
        """
        Computes a live neighbours matrix A of the game grid of size N x N and updates its
        as instance variable. A[i][j] expresses how many neighbors the cell [i][j] of the current
        Game grid has.
        """

        # loop over whole grid
        for i in range(self.N):
            for j in range(self.N):

                number_of_live_neighbours = 0  # total number of live neighbours

                # loop over all neighbours
                for x in [i - 1, i, i + 1]:
                    for y in [j - 1, j, j + 1]:

                        if (x == i and y == j):
                            continue  # skip current point, only count neighbours

                        if (x != self.N and y != self.N):
                            number_of_live_neighbours += self.old_grid[x][y]

                        # remaining branches handle the case where the neighbour is off the end of the grid
                        # in this case, we loop back round such that the grid becomes a "toroidal array"
                        elif (x == self.N and y != self.N):
                            number_of_live_neighbours += self.old_grid[0][y]
                        elif (x != self.N and y == self.N):
                            number_of_live_neighbours += self.old_grid[x][0]
                        else:
                            number_of_live_neighbours += self.old_grid[0][0]

                # store number of neighbours in corresponding matrix
                self.live_neighbours_grid[i][j] = number_of_live_neighbours


    def update_grid_with_homomorphic_encryption(self, server_to_client_queue, client_to_server_queue):
        '''
        If homomorphic encryption is true, we use our simulated server realized by using threads and message queues
        to perform the update of the game based on the encrypted operation in the threaded server. This workaround has
        been chosen because the Pyseal instances such as Ciphertext() and Context() can't be serialized for a transfer using
        sockets.
        '''

        # compute live neighbour grid
        self.live_neighbours()
        print("[CLIENT/update_grid] live neighbour grid:")
        print(self.live_neighbours_grid)

        # encrypt old grid and live neighbour grid
        encrypted_old_grid = self.encryption.encrypt_old_grid(self.old_grid, self.N)
        encrypted_live_neighbours_grid = self.encryption.encrypt_live_neighbours_grid(self.live_neighbours_grid, self.N)

        # Put encrypted old grid and live neighbour in a dictionary to send to server as a message
        message = {"encrypted_old_grid": encrypted_old_grid,
                   "encrypted_live_neighbours_grid": encrypted_live_neighbours_grid}

        # send encrypted message to simulated server via queue
        client_to_server_queue.put(message)
        print("[CLIENT/update_grid] Put message into client to server queue")

        # waiting until get a reply in server to client queue
        while server_to_client_queue.qsize() == 0:
            print("[CLIENT/update_grid] Client thread waiting for server reply")
            time.sleep(0.001)

        # receive and fetch reply from server
        encrypted_new_grid = server_to_client_queue.get()
        print("[CLIENT/update_grid] fetch message from server to client queue")
        print("[CLIENT/update_grid] Encrypted Message received from simulated-server")

        # decrypt new grid and set it as the current/new grid of the game
        self.new_grid = self.encryption.decrypt_new_grid(encrypted_new_grid, self.N)
        print("[CLIENT/update_grid] decrypted new grid:")
        print(self.new_grid)

        # new configuration becomes the old configuration for the next generation.
        self.old_grid = self.new_grid


    def update_grid_without_homomorphic_encryption(self):
        '''
        If homomorphic encryption is not chosen, we can use are initial distributed architecture usuing TCP/Socket
        communication with a server.
        '''

        # Set up network communication parameter to communicate with remote server
        SERVER_ADRESS ="127.0.0.1"
        PORT = 12345

        # Establish connection to remote server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #get client socket
        client_socket.connect((SERVER_ADRESS, PORT)) # connect to the server
        print("[CLIENT/update_grid] Client connection established at ", SERVER_ADRESS,":",PORT)

        # Serialize current grid state as byte string for sever transmission
        with BytesIO() as b:
            np.save(b, self.old_grid)
            old_grid_serialized = b.getvalue()
        print("[CLIENT/update_grid] Grid serialized for socket communication")

        # measure size of the message to ensure that server receives the whole message
        size=sys.getsizeof(old_grid_serialized)
        print("[CLIENT/update_grid] Size of the message in bytes: ", size)

        # send to server
        out = old_grid_serialized
        client_socket.sendall(out)
        print("[CLIENT/update_grid] Message sent to server via socket")

        #Sever answer is the new grid state as a bytestream
        answer_from_server = Helper.receive_complete_bytestream(client_socket, MESSAGE_SIZE=size, MAX_BUFFER_SIZE=65536)

        try:
            grid_by_server = np.load(BytesIO(answer_from_server)) #deserialize byte server reply to a np array
            print("[CLIENT/update_grid] Server Reply:\n", grid_by_server)
        except ValueError:
            print("[CLIENT/update_grid] Value error occured")

        print("[CLIENT/update_grid] Not-encrypted message received from server")
        print("[CLIENT/update_grid] decrypted new grid:")
        print(self.new_grid)

        #update grid states
        self.new_grid = grid_by_server
        self.old_grid = self.new_grid

        #close connection after message received
        client_socket.close()


    def update_grid(self, server_to_client_queue, client_to_server_queue, homomorphic_encryption):
        '''
        updates the grid of the game depending on the boolean homomorphic_encryption parameter either using homomorphic encryption on a
        threaded simulated server or directly computing the next grid using a (remote) socket TCP server

        :param server_to_client_queue: Queue used for communication from server to client
        :param client_to_server_queue:  Queue used for communication from client to (simulated) server
        :param homomorphic_encryption: Boolean variable; True of homomorphic encryption is ticked and should be used for the grid update
        :return:
        '''

        print("[CLIENT/update_grid] old grid:")
        print(self.old_grid)

        if (homomorphic_encryption == True):
            # homomorphic encryption uses simulated server via thread
            self.update_grid_with_homomorphic_encryption(server_to_client_queue, client_to_server_queue)
        else:
            # normal grid update is done via socket server
            self.update_grid_without_homomorphic_encryption()


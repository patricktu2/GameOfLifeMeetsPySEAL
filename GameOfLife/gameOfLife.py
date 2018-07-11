#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Kathrin

"""

import numpy
import random
import encryption
import time


class GameOfLife:

    def __init__(self, N):
        """ Set up Conway's Game of Life. """

        # dimension of grid (N*N = number of cells)
        self.N = N
        # matrix representing old generation
        self.old_grid = numpy.zeros(N * N, dtype='i').reshape(N, N)
        # matrix representing new generation
        self.new_grid = numpy.zeros(N * N, dtype='i').reshape(N, N)
        # matrix to store live neighbours of each cell
        self.live_neighbours_grid = numpy.zeros(N * N, dtype='i').reshape(N, N)

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

    def update_grid(self, server_to_client_queue, client_to_server_queue):
        '''
        updates the grid of the game using homomprhpic encryption. Computation is done by a
        simulated threaded server via queue communication
        :param server_to_client_queue: Queue used for communication from server to client
        :param client_to_server_queue:  Queue used for communication from client to (simulated) server
        :return:
        '''

        print("[CLIENT]old grid:")
        print(self.old_grid)

        # compute live neighbour grid
        self.live_neighbours()
        print("[CLIENT] live neighbour grid:")
        print(self.live_neighbours_grid)

        # encrypt old grid and live neighbour grid
        encrypted_old_grid = self.encryption.encrypt_old_grid(self.old_grid, self.N)
        encrypted_live_neighbours_grid = self.encryption.encrypt_live_neighbours_grid(self.live_neighbours_grid, self.N)

        # Put encrypted old grid and live neighbour in a dicitonary to send to server as a massage
        message = {"encrypted_old_grid": encrypted_old_grid,
                   "encrypted_live_neighbours_grid": encrypted_live_neighbours_grid}

        # send encrypted message to simulated server via queue
        client_to_server_queue.put(message)
        print("[CLIENT] Put message into client to server queue")

        # waiting until get a reply in server to client queue
        while server_to_client_queue.qsize() == 0:
            print("[CLIENT] Client thread waiting for server reply")
            time.sleep(0.1)

        # receive and fetch reply from server
        encrypted_new_grid = server_to_client_queue.get()
        print("[CLIENT] fetch message from server to client queue")
        print("[CLIENT] Message received from server:", encrypted_new_grid)

        # decrypt new grid and set it as the current/new grid of the game
        self.new_grid = self.encryption.decrypt_new_grid(encrypted_new_grid, self.N)
        print("[CLIENT] decrypted new grid:")
        print(self.new_grid)

        # new configuration becomes the old configuration for the next generation.
        self.old_grid = self.new_grid

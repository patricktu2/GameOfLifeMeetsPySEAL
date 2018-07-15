#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: Patrick Tu & Kathrin Witzlsperger


'''

import numpy as np
import socket
from threading import Thread
import traceback
import sys
from io import BytesIO
from time import gmtime, strftime
from GameOfLife.helper import Helper


# This server is started in parallel with the client. For the extension of the functionality,
# the homomorphic operations could be further implemented in this class once the issues
# of serializing PySEAL objects (i.e. Ciphertext and Context) are resolved. There were already github
# issues regarding that issued. Currently the server just supports the non-homomorphic-encrypted
# operations to compute the next state of the game of live.


class gol_methods:
    '''
    Consist the methods to update the grid based on the rules
    of Conway's game of life
    '''

    @staticmethod
    def live_neighbours(i, j, old_grid):
        """
        Count the number of live neighbours around point (i, j). In total all
        8 adjacent cells are assessed.
        """
        s = 0 # The total number of live neighbours.
        N = len(old_grid)

        # Loop over all the neighbours.
        for x in [i-1, i, i+1]:
            for y in [j-1, j, j+1]:
                if(x == i and y == j):
                    continue # Skip the current point itself - we only want to count the neighbours!
                if(x != N and y != N):
                    s += old_grid[x][y]
                # The remaining branches handle the case where the neighbour is off the end of the grid.
                # In this case, we loop back round such that the grid becomes a "toroidal array".
                elif(x == N and y != N):
                    s += old_grid[0][y]
                elif(x != N and y == N):
                    s += old_grid[x][0]
                else:
                    s += old_grid[0][0]
        return s

    @staticmethod
    def update_grid(old_grid):
        """
        Updates a N X N numpy array / grid by looping over each
        cell of the grid and apply Conway's rules
        Returns the new Numpy Array
        """

        N = len(old_grid)

        new_grid = np.zeros(N*N, dtype='i').reshape(N,N) # I THINK HERE IS THE ERROR
        for i in range(N):
            for j in range(N):
                live = gol_methods.live_neighbours(i, j, old_grid)
                if(old_grid[i][j] == 1 and live < 2):
                    new_grid[i][j] = 0 # Dead from starvation.
                elif(old_grid[i][j] == 1 and (live == 2 or live == 3)):
                    new_grid[i][j] = 1 # Continue living.
                elif(old_grid[i][j] == 1 and live > 3):
                    new_grid[i][j] = 0 # Dead from overcrowding.
                elif(old_grid[i][j] == 0 and live == 3):
                    new_grid[i][j] = 1 # Alive from reproduction.

        print("[SERVER] New Grid State computed")
        return new_grid

class Server:

    def client_thread(self,conn, ip, port, MAX_BUFFER_SIZE = 65536):
        '''
        Thread starts when a client dials in
        :param conn: Connection
        :param ip: Ip adress of client
        :param port: Port
        :param MAX_BUFFER_SIZE: maximum byte size of a processed message until exception is thrown
        :return:
        '''
        print("[SERVER] Server Thread started")

        # sockets don't know if the whole msg has been transmitted, hence check for fixed msg size
        # msg size depends on the board size, byte size of 100x100 grid is 40113; Byte size of 15x15 grid is 1013
        MESSAGE_SIZE = 1061 # This is hard coded for our demo purpose
        input_from_client_bytes = Helper.receive_complete_bytestream(conn, MESSAGE_SIZE, MAX_BUFFER_SIZE)
    
        print("[SERVER] Input from client received competely")
        print(input_from_client_bytes)

        # MAX_BUFFER_SIZE is how big the message can be
        # this is test if it's sufficiently big
        siz = sys.getsizeof(input_from_client_bytes)
        print("[SERVER] Size of whole received package is ", siz)
        if  siz >= MAX_BUFFER_SIZE:
            print("[SERVER] The length of input is probably too long: {}".format(siz))
    
        # deserialize input as it is a pickled np array
        try:
            input_from_client = np.load(BytesIO(input_from_client_bytes))
            print("[SERVER] Message deserialized")
        except ValueError:
            print("[SERVER] Value error occured")
    
        print("[SERVER] Grid received \n",input_from_client)
    
        # update the grid by calling the method from gol_methods
        old_grid = input_from_client
        new_grid = gol_methods.update_grid(old_grid)

        #serialize reply
        with BytesIO() as b:
            np.save(b, new_grid)
            new_grid_serialized = b.getvalue()

        #send reply
        out = new_grid_serialized
        conn.sendall(out)  # send it to client
        conn.close()  # close connection
        print('Connection ' + ip + ':' + port + " ended")
    
    def start_server(self):
        '''
        Starts the server and license at the port, starts thread if a client connects
        :return:
        '''

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this is for easy starting/killing the app
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('[SERVER] Socket created')
    
        #Specify server adress
        server_adress ="127.0.0.1"
        port = 12345
    
        try:
            server_socket.bind((server_adress, port))
            print('[SERVER] Socket bind complete')
        except socket.error as msg:
            print('[SERVER] Bind failed. Error : ' + str(sys.exc_info()))
            sys.exit()
    
        #Start listening on socket
        server_socket.listen(10)
        print('[SERVER] Socket now listening 127.0.0.1:12345')
    
        # for handling task in separate jobs we need threading
        # this will make an infinite loop needed for 
        # not resetting server for every client
        while True:
            conn, addr = server_socket.accept()
            ip, port = str(addr[0]), str(addr[1])
            print('[SERVER] Accepting connection from ' + ip + ':' + port)
            try:
                Thread(target=self.client_thread, args=(conn, ip, port)).start()
            except:
                print("[SERVER] Terible error!")
                traceback.print_exc()
        server_socket.close()


# --------------------- START MAIN -------------------------
if __name__== '__main__':
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    server = Server()
    server.start_server()
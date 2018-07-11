#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: Patrick 

'''

import pickle
import numpy as np
import socket
from threading import Thread
import traceback
import sys
import random
from io import BytesIO
from time import gmtime, strftime


class Server:
    
    def receive_complete_bytestream(self,conn,MESSAGE_SIZE, MAX_BUFFER_SIZE):
        '''
        Handles receiving data bytestream of server side sockets so that it is
        complete based on a fixed byte size and returns the byte string
        '''
        bytes_received = 0
        # start with empty byte message
        input_from_client_bytes = b''
    
        #QUOTE FROM DOCUMENTATION:
        #"Now we come to the major stumbling block of sockets - send and recv operate on the network buffers.
        # They do not necessarily handle all the bytes you hand them (or expect from them), [...]"
        # Hence while loop to ensure we get the whole byte stream to deserialize
        while bytes_received < MESSAGE_SIZE:
            # receive bytestream from socket connection
            current_input = conn.recv(MAX_BUFFER_SIZE)
            #if we receive an empty message something is odd
            if current_input == b'':
                raise RuntimeError("socket connection broken")
    
            # Did we receive the whole message? How much did we receive?
            current_input_size = sys.getsizeof(current_input)
            print(current_input_size, " bytes received")
            #Update size condition to exit the loop
            bytes_received = bytes_received + current_input_size
            #appending current input to whole input byte message
            input_from_client_bytes = input_from_client_bytes + current_input
    
        return input_from_client_bytes
    
    def client_thread(self,conn, ip, port, MAX_BUFFER_SIZE = 65536):
        '''
        Thread starts when a client dials in
        :param conn:
        :param ip:
        :param port:
        :param MAX_BUFFER_SIZE:
        :return:
        '''
        print("Server Thread startet")
    
        # sockets don't know if the whole msg has been transmitted, hence check for fixed msg size
        # msg size depends on the board size, byte size of 100x100 grid is 40113
        MESSAGE_SIZE = 40113
    
        input_from_client_bytes = receive_complete_bytestream(conn,MESSAGE_SIZE, MAX_BUFFER_SIZE)
    
        print("Input from client received competely")
    
        print(input_from_client_bytes)
        # MAX_BUFFER_SIZE is how big the message can be
        # this is test if it's sufficiently big
        siz = sys.getsizeof(input_from_client_bytes)
        print("Size of whole received package is ", siz)
        if  siz >= MAX_BUFFER_SIZE:
            print("The length of input is probably too long: {}".format(siz))
    
        # deserialize input as it is a pickled np array
        print("Received input deserialized")
    
        try:
            #input_from_client = pickle.loads(input_from_client_bytes, fix_imports=False)
            input_from_client = np.load(BytesIO(input_from_client_bytes))
            #print("Input:\n", input_from_client)
        except ValueError:
            print("Value error occured")
    
    
        print("Grid received \n",input_from_client)
    
        #process Input somehow, next board state to be implemented
        old_grid = input_from_client
        new_grid = old_grid
        #new_grid = gol_methods.update_grid(old_grid)
        #print(new_grid)
    
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
        print('Socket created')
    
        #Specify server adress
        server_adress ="127.0.0.1"
        port = 12345
    
        try:
            server_socket.bind((server_adress, port))
            print('Socket bind complete')
        except socket.error as msg:
            print('Bind failed. Error : ' + str(sys.exc_info()))
            sys.exit()
    
        #Start listening on socket
        server_socket.listen(10)
        print('Socket now listening 127.0.0.1:12345')
    
        # for handling task in separate jobs we need threading
    
        # this will make an infinite loop needed for 
        # not reseting server for every client
        while True:
            conn, addr = server_socket.accept()
            ip, port = str(addr[0]), str(addr[1])
            print('Accepting connection from ' + ip + ':' + port)
            #try:
                #Thread(target=client_thread, args=(conn, ip, port)).start()
            #except:
                #print("Terible error!")
                #traceback.print_exc()
        server_socket.close()

if __name__== '__main__':
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    server = Server()
    server.start_server()
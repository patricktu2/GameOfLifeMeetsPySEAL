#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Kathrin

"""

import tkinter
import time
from time import gmtime, strftime
import threading
import queue
import gameOfLife
from server_simulation import Threaded_server

class Gui:
    def __init__(self, dim, root, queue, startCommand, stopCommand):


        self.queue = queue
        
        self.dim = dim
        
        # grid on canvas
        self.canvas = tkinter.Canvas(root,
                                     width=self.dim*15,
                                     height=self.dim*15,
                                     background='white')
        self.canvas.grid(row=0, column=1)
        self.rect = [[None for row in range(self.dim)] for col in range(self.dim)]
        for row in range(self.dim):
            for col in range(self.dim):
                self.rect[row][col] = self.canvas.create_rectangle(row*15, col*15,
                                                                  (row+1)*15,
                                                                  (col+1)*15,
                                                                  width=1,
                                                                  fill='white',
                                                                  outline='white')
        # start and stop button
        frame = tkinter.Frame(root)
        frame.grid(row=0, column=0)
        start_button = tkinter.Button(frame,
                                      text="Start",
                                      command=startCommand)                
        start_button.pack()
        stop_button = tkinter.Button(frame,
                                     text="Stop",
                                     command=stopCommand)
        stop_button.pack()

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                
                for row in range(self.dim):
                    for col in range(self.dim):
                        if msg[row][col] == 1:
                            self.canvas.itemconfig(self.rect[row][col],
                                                   fill='blue',
                                                   outline='grey')
                        if msg[row][col] == 0:
                            self.canvas.itemconfig(self.rect[row][col],
                                                   fill='white',
                                                   outline='white')
                self.canvas.update()
            except queue.Empty:
                print("empty queue")


class ThreadedClient:
   
    def __init__(self, dim, root):

        self.root = root
        
        # dimension of grid
        self.dim = dim

        # create the queue
        self.queue = queue.Queue()

        # set up the GUI
        self.gui = Gui(self.dim,
                       self.root,
                       self.queue,
                       self.startApplication,
                       self.stopApplication)
        
        self.running = 0

        # start periodic call in the GUI to check if the queue contains anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        if self.running:
            self.gui.processIncoming()
        if not self.running:
            print("[CLIENT] Not running")
        self.root.after(200, self.periodicCall)

    def workerThread(self):
        game = gameOfLife.GameOfLife(self.dim)

        # create queue for simulated client server communication
        self.server_to_client_queue = queue.Queue() #queue sending messages to server
        self.client_to_server_queue = queue.Queue() #queue receiving from server
        server = Threaded_server(dim,self.server_to_client_queue, self.client_to_server_queue, game.encryption.context)
        server.start() # start server as a thread

        generation = 0
        while self.running:
            print("generation", generation)
            if generation == 0:
                msg = game.old_grid
            else:
                time.sleep(0.25)
                game.update_grid(self.server_to_client_queue, self.client_to_server_queue)
                msg = game.new_grid
            generation += 1
            self.queue.put(msg)

    def stopApplication(self):
        self.running = 0
        with self.queue.mutex:
            self.queue.queue.clear()
        print("[CLIENT] Application stopped")

    def startApplication(self):
        if self.running == 1:
            print("[CLIENT] already running")
            return
        self.running = 1
        self.thread = threading.Thread(target=self.workerThread)
        self.thread.setDaemon(True)
        self.thread.start()
        print("[CLIENT] Application started")

if __name__== '__main__':
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    
    root = tkinter.Tk()
    root.title('Conway\'s Game of Life')
    # dimension of grid
    dim = 15
    client = ThreadedClient(dim, root)
    root.mainloop()

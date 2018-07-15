#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Patrick Tu & Kathrin Witzlsperger

"""

import tkinter
from tkinter import *
import time
from time import gmtime, strftime
import threading
import queue
import gameOfLife
from server_simulation import Threaded_server

class Gui:
    def __init__(self, dim, root, queue, startCommand, stopCommand):
        """
        Set up GUI elements consisting of start and stop button,
        checkbox to select encryption
        and canvas element to visualize Game of Life.
        """

        self.queue = queue

        # dimension of grid (number of cells = dim*dim)
        self.dim = dim

        frame = tkinter.Frame(root)
        frame.pack()

        # canvas element for visualization of grid
        self.canvas = tkinter.Canvas(frame,
                                     width=self.dim*30,
                                     height=self.dim*30,
                                     background='white')
        self.canvas.pack()

        # list of rectangles (= cells) on canvas element
        self.rect = [[None for row in range(self.dim)] for col in range(self.dim)]
        for row in range(self.dim):
            for col in range(self.dim):
                self.rect[row][col] = self.canvas.create_rectangle(row*30, col*30,
                                                                   (row+1)*30,
                                                                   (col+1)*30,
                                                                   width=1,
                                                                   fill='white',
                                                                   outline='white')

        bottomframe = tkinter.Frame(root)
        bottomframe.pack(side = tkinter.BOTTOM)

        # start button
        start_button = tkinter.Button(bottomframe,
                                      text="Start",
                                      command=startCommand)
        start_button.pack(ipadx=7, side=tkinter.LEFT)

        # stop button
        stop_button = tkinter.Button(bottomframe,
                                     text="Stop",
                                     command=stopCommand)
        stop_button.pack(ipadx=7, padx= 5, side=tkinter.LEFT)

        # option to use the application with or without homomorphic encryption as a check box
        self.homomorphic_encryption = tkinter.BooleanVar()
        self.homomorphic_encryption.set(True)  # default is True
        checkbox = tkinter.Checkbutton(root, text = "homomorphic encryption", variable = self.homomorphic_encryption)
        checkbox.pack()


    def processIncoming(self):
        """Handle all messages (newly computed generations) currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # draw new grid generation
                for row in range(self.dim):
                    for col in range(self.dim):
                        if msg[row][col] == 1:
                            # draw corresponding canvas rectangle (= cell) blue (= live)
                            self.canvas.itemconfig(self.rect[row][col],
                                                   fill='blue',
                                                   outline='grey')
                        if msg[row][col] == 0:
                            # draw corresponding canvas rectangle (= cell) white (= dead)
                            self.canvas.itemconfig(self.rect[row][col],
                                                   fill='white',
                                                   outline='white')
                self.canvas.update()
            except queue.Empty:
                print("empty queue")


class ThreadedClient:
   
    def __init__(self, dim, root):
        """
        Set up threaded client by initializing message queue and GUI.
        """

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

        # variable to control if Conway's Game of Life is running (= button start was last button that was pressed)
        # default value is 0 (= not running)
        self.running = 0

        # start periodic call in the GUI to check if the queue contains anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue
        if Game of Life is runnning.
        """
        if self.running:
            self.gui.processIncoming()
        if not self.running:
            print("[CLIENT / GUI] Not running")
        self.root.after(200, self.periodicCall)

    def workerThread(self):
        '''
        Creates a new GameOfLife board and starts an infinite loop where the state
        of the will be iteratively updated by calling a update method
        '''

        # create new game
        game = gameOfLife.GameOfLife(self.dim)

        # create queue for simulated client server communication
        self.server_to_client_queue = queue.Queue() #queue sending messages to server
        self.client_to_server_queue = queue.Queue() #queue receiving from server
        server = Threaded_server(dim,self.server_to_client_queue, self.client_to_server_queue, game.encryption.context)
        server.start() # start server as a thread

        generation = 0

        while self.running:
            print("[CLIENT / GUI] Generation", generation)
            print("[CLIENT / GUI] Homomorphic encryption == ", self.gui.homomorphic_encryption.get())
            if generation == 0:
                # grid initialization
                msg = game.old_grid
            else:
                # compute new grid state
                time.sleep(0.1)
                game.update_grid(self.server_to_client_queue, self.client_to_server_queue, self.gui.homomorphic_encryption.get())
                msg = game.new_grid
            generation += 1
            # add to message queue and hand it over to GUI to visualize it
            self.queue.put(msg)

    def stopApplication(self):
        '''
        Gets executed when the stop button is pressed.
        Stops currently running Game of Life.
        Cleans up message queue.
        '''

        self.running = 0
        with self.queue.mutex:
            self.queue.queue.clear()
        print("[CLIENT / GUI] Application stopped")

    def startApplication(self):
        '''
        Gets executed when the start button is pressed. Starts the application by creating
        a worker thread and starting it
        '''

        if self.running == 1:
            print("[CLIENT / GUI] already running")
            return
        self.running = 1
        self.thread = threading.Thread(target=self.workerThread)
        self.thread.setDaemon(True)
        self.thread.start()
        print(" [CLIENT / GUI] Application started")


# --------------------- START MAIN -------------------------
if __name__== '__main__':
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    
    root = tkinter.Tk()
    root.title('Conway\'s Game of Life')
    # dimension of grid
    dim = 15
    client = ThreadedClient(dim, root)
    root.mainloop()

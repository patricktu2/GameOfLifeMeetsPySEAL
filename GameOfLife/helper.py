import sys


class Helper:
    '''
    provides helper method for the server and client monnunication via sockets
    to receive bytestreams
    '''

    @staticmethod
    def receive_complete_bytestream(conn, MESSAGE_SIZE, MAX_BUFFER_SIZE):
        '''
        Handles receiving data bytestream of server side sockets so that it is
        complete based on a fixed byte size and returns the byte string
        '''

        bytes_received = 0
        # start with empty byte message
        input_from_client_bytes = b''

        # QUOTE FROM DOCUMENTATION:
        # "Now we come to the major stumbling block of sockets - send and recv operate on the network buffers.
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
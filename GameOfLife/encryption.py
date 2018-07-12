#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Patrick Tu & Kathrin Witzlsperger
"""
import numpy
import seal
from seal import EncryptionParameters, \
                 Encryptor,            \
                 IntegerEncoder,       \
                 KeyGenerator,         \
                 Ciphertext,           \
                 Decryptor,            \
                 Plaintext,            \
                 SEALContext

class Encryption:
    '''
    Provides encryption / encoding methods to realize the homomorphic operations
    '''

    
    def __init__(self):

        # set parameters for encryption
        parms = EncryptionParameters()
        parms.set_poly_modulus("1x^2048 + 1")
        parms.set_coeff_modulus(seal.coeff_modulus_128(2048))
        parms.set_plain_modulus(1 << 8)
       
        self.context = SEALContext(parms)
        keygen = KeyGenerator(self.context)
        self.encoder = IntegerEncoder(self.context.plain_modulus())
      
        public_key = keygen.public_key()
        self.encryptor = Encryptor(self.context, public_key)
      
        secret_key = keygen.secret_key()
        self.decryptor = Decryptor(self.context, secret_key)
      
        
      
    def encrypt_live_neighbours_grid(self, live_neighbours_grid, dim):
        '''
        Encodes the live neighbor matrix by applying following rules. If the cell [i][j] has 2 neighbors with 0,
        3 neighbors with 2, and otherwise with -2. Afterwards encrypt it using PySEAL and store in a list

        :param live_neighbours_grid: live neighbor matrix as np array
        :param dim: dimension of the board
        :return: List of encoded and encrypted neighbors
        '''

        encrypted_live_neighbours_grid = []

        # Loop through every element of the board and encrypt it
        for i in range(dim):
           for j in range(dim):
               # transformation / encoding rules
               if(live_neighbours_grid[i][j] == 2):
                   value = 0
               elif(live_neighbours_grid[i][j] == 3):
                    value = 2
               elif(live_neighbours_grid[i][j] > 3 or live_neighbours_grid[i][j] < 2):
                    value = -2
                
               # element-wise homomorphic encryption
               encrypted = Ciphertext()
               plain = self.encoder.encode(value)
               self.encryptor.encrypt(plain, encrypted)
               encrypted_live_neighbours_grid.append(encrypted)
                
        return encrypted_live_neighbours_grid
    
    def encrypt_old_grid(self, old_grid, dim):
        '''
        Encrypts each element in the old board state using PySEAL and adds it to a list

        :param old_grid:
        :param dim:
        :return:
        '''
        
        encrypted_old_grid = []

        # Loop through every element of the board and encrypt it
        for i in range(dim):
            for j in range(dim):
                # element-wise homomorphic encryption
                encrypted = Ciphertext()
                value = old_grid[i][j]
                plain = self.encoder.encode(value)
                self.encryptor.encrypt(plain, encrypted)
                encrypted_old_grid.append(encrypted)
               
        return encrypted_old_grid
    
    def decrypt_new_grid(self, encrypted_new_grid, dim):
        '''
        Decrypts a homomorphic-encrypted grid by looping through every element,
        decrypt it and then applying the decoding rules to get the new board state

        :param encrypted_new_grid:
        :param dim:
        :return:
        '''

        new_grid = numpy.zeros(dim*dim, dtype='i').reshape(dim,dim)
        
        for i in range(dim):
          for j in range(dim):
              plain = Plaintext()
              
              encrypted = encrypted_new_grid[dim*i + j]
                  
              self.decryptor.decrypt(encrypted, plain)
              value = self.encoder.decode_int32(plain)
              
              # transformation / decoding rules
              if(value <= 0):
                  new_grid[i][j] = 0
              elif(value > 0):
                  new_grid[i][j] = 1
              
        return new_grid
        

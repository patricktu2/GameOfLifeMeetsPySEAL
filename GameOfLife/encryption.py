#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Kathrin
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
        
        encrypted_live_neighbours_grid = []
        
        for i in range(dim):
           for j in range(dim):
               
               # transformation
               if(live_neighbours_grid[i][j] == 2):
                   value = 0
               elif(live_neighbours_grid[i][j] == 3):
                    value = 2
               elif(live_neighbours_grid[i][j] > 3 or live_neighbours_grid[i][j] < 2):
                    value = -2
                
               # homomorphic encryption
               encrypted = Ciphertext()
               plain = self.encoder.encode(value)
               #print("Encoded " + (str)(value) + " as polynomial " + plain.to_string() + " (live neighbour grid)") 
               self.encryptor.encrypt(plain, encrypted)
               encrypted_live_neighbours_grid.append(encrypted)
                
        return encrypted_live_neighbours_grid
    
    def encrypt_old_grid(self, old_grid, dim):
        
        encrypted_old_grid = []
       
        for i in range(dim):
            for j in range(dim):
                # homomorphic encryption
                encrypted = Ciphertext()
                value = old_grid[i][j]
                plain = self.encoder.encode(value)
                #print("Encoded " + (str)(value) + " as polynomial " + plain.to_string() + " (old grid)")
                self.encryptor.encrypt(plain, encrypted)
                encrypted_old_grid.append(encrypted)
               
        return encrypted_old_grid
    
    def decrypt_new_grid(self, encrypted_new_grid, dim):
        
        new_grid = numpy.zeros(dim*dim, dtype='i').reshape(dim,dim)
        
        for i in range(dim):
          for j in range(dim):
              plain = Plaintext()
              
              encrypted = encrypted_new_grid[dim*i + j]
                  
              self.decryptor.decrypt(encrypted, plain)
              value = self.encoder.decode_int32(plain)
              
              # transformation
              if(value <= 0):
                  new_grid[i][j] = 0
              elif(value > 0):
                  new_grid[i][j] = 1
              
        return new_grid
        

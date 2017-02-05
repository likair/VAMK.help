# -*- coding: utf-8 -*-
"""
    vamk.utils.encryption
    ~~~~~~~~~~~~~~~~~~~~~
    Implements encryption and decryption functions.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

from Crypto.Cipher import AES


class Encryption:
    """Includes two static methods for encrypting and decrypting the text. Would be used to encrypt the student
    credentials to store in the database.
    """
    #  The secret key to use in the symmetric cipher. It must be 16 (AES-128), 24 (AES-192), or 32 (AES-256) bytes long.
    KEY = 'VAMK YOUSELF!!!#'
    # The initialization vector to use for encryption or decryption.
    IV = 'VAMK MYSELF!!!##'
    # The chaining mode to use for encryption or decryption.
    MOD = AES.MODE_CFB

    def __init__(self):
        pass

    @staticmethod
    def encrypt(plaintext):
        """Encrypts the plaintext.

        :param plaintext: string

        :return: ciphertext: string
        """
        cipher = AES.new(Encryption.KEY, Encryption.MOD, Encryption.IV)
        ciphertext = cipher.encrypt(plaintext).encode('hex')
        return ciphertext

    @staticmethod
    # Decryption
    def decrypt(ciphertext):
        """Decrypts the ciphertext.

        :param ciphertext: string

        :return: plaintext: string
        """
        cipher = AES.new(Encryption.KEY, Encryption.MOD, Encryption.IV)
        plaintext = cipher.decrypt(ciphertext.decode('hex'))
        return plaintext

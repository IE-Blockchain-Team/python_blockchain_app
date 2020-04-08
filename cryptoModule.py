import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

# encrypt
def encrypt(rsa_publickey,plain_text):
     cipher_text=rsa_publickey.encrypt(plain_text,32)[0]
     b64cipher=base64.b64encode(cipher_text)
     return b64cipher

# decrypt
def decrypt(rsa_privatekey,b64cipher):
     decoded_ciphertext = base64.b64decode(b64cipher)
     plaintext = rsa_privatekey.decrypt(decoded_ciphertext)
     return plaintext

# Key pair generation
def rsakeys():  
     length=1024  
     privatekey = RSA.generate(length, Random.new().read)  
     publickey = privatekey.publickey()  
     return privatekey, publickey

# Signing a message
def sign(privatekey,data):
     h = SHA256.new(data)  #data.encode()  <- removed since we are now passing a bytearray object
     return pkcs1_15.new(privatekey).sign(h)
     #return base64.b64encode(str(pkcs1_15.new(privatekey).sign(h)).encode())
    #return base64.b64encode(str((privatekey.sign(data,''))[0]).encode())

# Verify a message
def verify(publickey,data,sign):
     data = SHA256.new(data)
     return pkcs1_15.new(publickey).verify(data, sign)
     #return publickey.verify(data,sign)
     #return publickey.verify(data,(int(base64.b64decode(sign))))

# Import an RSA key from file?
def importKey(externKey):
    return RSA.importKey(externKey)
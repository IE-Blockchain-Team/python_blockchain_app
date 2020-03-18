import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import base64

# Key pair generation
def rsakeys():  
     length=1024  
     privatekey = RSA.generate(length, Random.new().read)  
     publickey = privatekey.publickey()  
     return privatekey, publickey

# Signing a message
def sign(privatekey,data):
    return base64.b64encode(str((privatekey.sign(data,''))[0]).encode())

# Verify a message
def verify(publickey,data,sign):
     return publickey.verify(data,(int(base64.b64decode(sign)),))
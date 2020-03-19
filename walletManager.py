from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
import cryptoModule
import os.path
import time



while (True):
    option = input("Wallet Manager, Select Option:\n1-Create Key Pair and save to wallet\n2-Open Wallet\n3-Exit\nOption:")
    if (option == '1'):
        password = input("Give a password:")
        key = RSA.generate(2048)
        privKey = key.export_key()
        pubKey = key.publickey().export_key()
        print("private key: " + str(privKey) + "\n length: " + str(len(privKey)) + '\n')
        print("public key: " + str(pubKey) + "\n length: " + str(len(pubKey)) + '\n')
        string = privKey + pubKey
        salt = get_random_bytes(16)
        print("salt: " + str(salt) + " length: " + str(len(salt)))
        keys = PBKDF2(password, salt, 64, count=1000000, hmac_hash_module=SHA512)
        key1 = keys[:32]
        #key2 = keys[32:]
        cipher = AES.new(key1, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(string)
        ciphertext += salt
        print(ciphertext[-16:])
        
        
        if os.path.isfile('wallet.bin'):
            print("Found existing wallet.bin")
            counter = 0
            while (os.path.isfile('wallet{}.bin'.format(counter))):
                time.sleep(0.5)
                counter += 1
            newWalletName = 'wallet{}.bin'.format(counter)
        else:
            print("No wallet found, creating new wallet")
            newWalletName = 'wallet.bin'
        file_out = open(newWalletName, "wb")
        #print(cipher.nonce)
        #print(tag)
        #print(ciphertext)
        for x in (cipher.nonce, tag, ciphertext):
            file_out.write(x)
        file_out.close()
        print("Wallet saved as: ", newWalletName)
    elif (option == '2'):
        walletName = input("Name of wallet to open:")
        password = input("Password:")
        fileIn = open(walletName, "rb")
        nonce, tag, ciphertext = [ fileIn.read(x) for x in (16, 16, -1) ]
        fileIn.close()
        keys = PBKDF2(password, ciphertext[-16:], 64, count=1000000, hmac_hash_module=SHA512)
        key1 = keys[:32]
        cipher = AES.new(key1, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext[:-16], tag)
        print("data: %s", data)
    elif (option == '3'):
        break
    else:
        print("Invalid Option...")
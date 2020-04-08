from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
import cryptoModule
import os.path
import time

import cryptoModule

def openWallet(walletName=None,password=None):
    if walletName is None:
        walletName = input("Name of wallet to open:")
    if password is None:
        password = input("Password:")
    fileIn = open(walletName, "rb")
    nonce, tag, ciphertext = [ fileIn.read(x) for x in (16, 16, -1) ]
    fileIn.close()
    keys = PBKDF2(password, ciphertext[-16:], 64, count=1000000, hmac_hash_module=SHA512)
    key1 = keys[:32]
    cipher = AES.new(key1, AES.MODE_EAX, nonce)
    try:
        data = cipher.decrypt_and_verify(ciphertext[:-16], tag)
    except ValueError:
        print("Invlaid password!")
        raise ValueError
    print("data: %s", data)
    return data

def createWallet():
    #privKey = key.export_key()
    #pubKey = key.publickey().export_key()
    # Generate Keys
    privKey, pubKey = cryptoModule.rsakeys()
    # Export our RSA private key so it can be saved to file  (RSA Public Key can always be generated from private key)
    privKey = privKey.export_key()
    pubKey = pubKey.export_key()
    print("private key: " + str(privKey) + "\n length: " + str(len(privKey)) + '\n')
    print("public key: " + str(pubKey) + "\n length: " + str(len(pubKey)) + '\n')
    # Generate a salt to use PBKDF2.  This will generate a key for our AES file encryption.
    salt = get_random_bytes(16)
    #print("salt: " + str(salt) + " length: " + str(len(salt)))
    password = input("Give a password:")
    keys = PBKDF2(password, salt, 64, count=1000000, hmac_hash_module=SHA512)
    #print(keys)
    key1 = keys[:32]
    #key2 = keys[32:]
    # Use the key generated from PBKDF2 to AES encrypt our RSA priv key
    cipher = AES.new(key1, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(privKey)
    # Append salt to ciphertext
    ciphertext += salt
    print("Wallet data successfully encrypted with AES using salted PBKDF2 key.")
    if os.path.isfile('wallet.bin'):
        counter = 0
        while (os.path.isfile('wallet{}.bin'.format(counter))):
            time.sleep(0.5)
            counter += 1
        newWalletName = 'wallet{}.bin'.format(counter)
    else:
        newWalletName = 'wallet.bin'
    file_out = open(newWalletName, "wb")
    #print(cipher.nonce)
    #print(tag)
    #print(ciphertext)
    for x in (cipher.nonce, tag, ciphertext):
        file_out.write(x)
    file_out.close()
    print("Wallet saved as: ", newWalletName)




if __name__ == '__main__':
    while (True):
        option = input("\n\nWallet Manager, Select Option:\n1-Create Key Pair and save to wallet\n2-Open Wallet\n3-Exit\nOption:")
        if (option == '1'):
            createWallet()
        elif (option == '2'):
            openWallet()
        elif (option == '3'):
            break
        else:
            print("Invalid Option...")
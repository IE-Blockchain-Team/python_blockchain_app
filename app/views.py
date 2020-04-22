import datetime
import json

import requests
import walletManager
import cryptoModule
from flask import render_template, redirect, request, flash

from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='Supply Chain Use Case Example',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    walletName = request.form["walletName"]
    password = request.form["password"]
    receiver = request.form["receiver"]
    
    # example for use case
    addrBook = {
        "farm_A": b"-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQChMJf/mB0mUtAIGHJLPeM1ZBk2\nq4vOtjmvlhoA4ZHpm6O9UJags5GELsxHk7my8WDOlb9fpgHM2hue6uY/a6QBuVus\n7ZIqKEm8D/Z9EF6nFxkAgD8tavuRYcDnOEkfRr7Gy7oAdtrbuoIuccu9gRQOpqex\nnYhLPm/d4EvgUEBNYQIDAQAB\n-----END PUBLIC KEY-----",
        "farm_B": b"-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDR7fbY0YixX0IqQHTIFAJOmPa4\n0MmFixcmYXPtA8zhlMbBAnYkIT2V1W6cthRwCcY3MtXJ2fyf5e+wcV8u5tgJ1POa\n0sPUF4ydPbCDh+wXq/5fumqxNH9pNa57b8CtsZMfiV51BbVgmYy1shp2VVoo8m8o\niBiVMq416lrilSBSwwIDAQAB\n-----END PUBLIC KEY-----",
        "delivery_A":b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCx4sgu15iWFv0gMrl19NSJ+Wyg\nNCOag2LjmlFTeYfUAlRenDSJJF7EC+NqmwVgVnKNd23CLQK44/zIQfy0LHp8Lf7o\nY5YdPBlARhGm8o0uRbNWMrrULoVP7dzQ36J5XGRJjVebOVd49crDrTKbGcCLw+5M\nwD8qEuzYsdR4vP6ZUwIDAQAB\n-----END PUBLIC KEY-----',
        "delivery_B": b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCd8sh6m6EihlSthqjOA/PiT5aG\nWj/XrRJXCmjNkQyDcwKSarB994bJmOgHZu6Q35dYYzge88S1cqLdxIbRdSCqlsRH\n+ZvMYbree462Kh85NJftxYi6UWxUek9ST89bpUNMa6Gd1RCc5BuDL8tTySSz2Mm8\nFI6AZpXGznQF86SLkwIDAQAB\n-----END PUBLIC KEY-----',
        "store_A":b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCdZeE+gpg+g2/d3khz/jsB8pRp\nOPyD1UqW4jpY6U/e+Roh+Ppkkd/BwK6WLvBkHGn1G6T7G9AacSSwnRjyJlD04bbb\necobrVlkVeI4OP+5l/q4el9Swz0O8mZ9yrVwuyTKvYvLsArDWxcdiCzgCoDOyFHb\nkUP+D1Vvh0Uz3Ky0BQIDAQAB\n-----END PUBLIC KEY-----',
        "store_B":b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDtSsNGEcLF3itjMk43Jvg/x2B\nL4SI7Z6Boyg1scFVT+GnIDyx2UijkTt2ZimKHPe0VLrPO4j8dCrhihW+Zz1qRmZR\nXnzfYb3kdt+BCgXg63t+uWIGfJbTRxss+TnjuyQdbwTrAvgtlqdpWe7e/uqvYl+w\nr59ryw8d9+OJ2FAD+QIDAQAB\n-----END PUBLIC KEY-----',
    }

    error = None
    
    if not post_content:
        error = "Must provide item data"
    elif not walletName:
        error = "Must provide walletName"
    elif not password:
        error = "Must provide wallet password"
    elif not receiver:
        error = "Must select a receiver to send the item to"
    else:
        # try to open wallet
        try:
            walletData = walletManager.openWallet(walletName, password)
        except ValueError:
            error = "Unable to open wallet due to invalid password"
    
    if error is None:
        # private key from wallet is read, now import
        importedPrivKey = cryptoModule.importKey(walletData)
        # this key can now be used to sign data, and also we can generate a public key
        importedPubKey = importedPrivKey.publickey()        
        # Signed Message Data Struct:  Message | Receiver
        signature = {
            "signedMessage": None,
            "receiver": None
        }

        signature["receiver"] = addrBook[receiver]

        post_content = bytearray(post_content, 'utf8')
        post_content = post_content + b'|' + signature["receiver"]
        
        print(post_content)
        print(post_content.decode('utf-8'))
        
        # sign the message being put into the tx (will be in base64 encoding)
        signature["signedMessage"] = cryptoModule.sign(importedPrivKey, post_content)  #A hash will be generated of the message, and that hash will be signed.  We can then verify signature, and then data integrity.
        print(signature["signedMessage"])
        print(cryptoModule.verify(importedPubKey, post_content, signature["signedMessage"]))

        post_object = {
            # public key of signee
            'senderPK': importedPubKey.exportKey().decode("utf-8"),
            # signed message
            'signature': signature["signedMessage"].decode('latin-1'),
            'data': post_content.decode('utf-8')
        }


        # Submit a transaction
        new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address,
                    json=post_object,
                    headers={'Content-type': 'application/json'})

        return redirect('/')

    # display error
    flash(error)
    return render_template('index.html', title='Supply Chain Use Case Example',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')

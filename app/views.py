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
        "delivery_A": b"-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDihpxy/szVtXY+eCfFB59Ho2n1\nU/ULgcXur+I7T4Aji0XDRyR79ueyz1u0HElkxkxiXXVKBUZFgt8PxYUxISQTu24Y\n9UaGBqjlXt/eCGA7e4CRohwqj73OCYELXQbIulHZrB+sRNDA5mgce0Vc5Nk4LpSV\neweJ6kR/W8dkQvqRuQIDAQAB\n-----END PUBLIC KEY-----"
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

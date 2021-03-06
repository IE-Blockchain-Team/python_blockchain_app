import json
import time

import os.path
from os import path

from flask import Flask, request
import requests

import blockchainClass as chainClass
import cryptoModule

import atexit

def create_chain_from_dump(chain_dump = None, noChain = False):
    generated_blockchain = chainClass.Blockchain()
    generated_blockchain.create_genesis_block()
    if not noChain:
        for idx, block_data in enumerate(chain_dump):
            #print(block_data)
            if idx == 0:
                continue  # skip genesis block
            block = chainClass.Block(block_data["index"],
                        block_data["transactions"],
                        block_data["timestamp"],
                        block_data["previous_hash"],
                        block_data["nonce"])
            proof = block_data['hash']
            added = generated_blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
    return generated_blockchain

# initialize the chain either by local_chain.txt or by creating the genesis block
def local_chain_exists():
    global blockchain
    if path.exists('local_chain.txt'):
        with open('local_chain.txt') as json_file:
            data = json.load(json_file)
            #print(data['chain'])
            return create_chain_from_dump(data['chain'])
    else:
        return create_chain_from_dump(noChain = True)

app = Flask(__name__)

# the node's copy of blockchain
blockchain = local_chain_exists()
#atexit.register(update_local_chain)

# the address to other participating members of the network
peers = set()

# endpoint to tell the server to save a copy of the current chain
@app.route('/save', methods=['GET'])
@atexit.register
def update_local_chain():
    with open('local_chain.txt', 'w') as f:
        f.write(get_chain())
    return "Success", 201

# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["senderPK", "signature", "data"]

    for field in required_fields:
        print(tx_data.get(field))
        if not tx_data.get(field):
            return "Invalid transaction data", 404
        
        if field == "signature":
            # Transaction validation process:
            # 1.  Verify the signature
            print(tx_data[field].encode('latin-1'))
            print("test")
            print(tx_data["senderPK"])
            print(tx_data["data"])
            #see if value_error exception is raised by cryptoModule.verify()
            valid_data = tx_data["signature"].encode('latin-1')
            #valid_data = bytearray(valid_data)
            #valid_data[0] = 5
            print(valid_data)
            importedPubKey = cryptoModule.importKey(tx_data["senderPK"])
            print(cryptoModule.verify(importedPubKey, bytearray(tx_data["data"], 'utf8'), valid_data))
            # 2.  Verify the data authenticity

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    #print(blockchain.chain)
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)}, indent=4)


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code

# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = chainClass.Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    viewable_unconfirmed_transactions = blockchain.unconfirmed_transactions
    for field in blockchain.unconfirmed_transactions:
        if field == "signature":
            viewable_unconfirmed_transactions["signature"] = blockchain.unconfirmed_transactions["signature"].encode("latin-1")
    
    return json.dumps(viewable_unconfirmed_transactions)


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False

def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

# Uncomment this line if you want to specify the port number in the code
#app.run(debug=True, port=8000)

# Blockchain client and server

A basic blockchain server and application written in python using Flask and Requests. Forked from this [guide](https://www.ibm.com/developerworks/cloud/library/cl-develop-blockchain-app-in-python/index.html)

## REST API Reference

### node_server.py (Full/Master Node)

| Action | Route | Path | Method
| --------- | --- | --- | --- |
| Save chain | /save | save a copy of the current chain locally | GET
| Mine block | /mine | tells the node to mine.  Needs to have pending unconfirmed transactions. | GET
| View chain | /chain | pulls copy of current chain and displays it in JSON format. | GET
| View pending tx's | /pending_tx | query unconfirmed transactions | GET
| Add peer | /register_with | add new peer to the network | POST
| Add block | /add_block | add a block mined by someone else to the node's chain | POST


### run_app.py (Basic Node / Front-end application)

| Action | Route | Description | Method
| --------- | --- | --- | --- |
| View main page | / | Allows for manual data submission, and shows a post for every block on the retrieved chain | GET
| Submit data | /submit | A submit button to manually submit/broadcast transaction data to localhost:8000 | POST

## Instructions to run


Install the dependencies,

```sh
> cd python_blockchain_app
> pip install -r requirements.txt
```

Start a blockchain node server:

For Windows
```sh
> set FLASK_APP=node_server.py
> flask run --port 8000
```

For Unix Bash
```sh
$ export FLASK_APP=node_server.py
$ flask run --port 8000
```

One instance of our blockchain node is now up and running at port 8000.


Run the application on a different terminal session,

```sh
$ python run_app.py
```

The application should be up and running at [http://localhost:5000](http://localhost:5000).



To play around by spinning off multiple custom nodes, use the `/register_with` endpoint to register a new node. 

Sample scenario:

```sh
# already running
$ flask run --port 8000 &
# spinning up new nodes
$ flask run --port 8001 &
$ flask run --port 8002 &
```

You can use the following cURL requests to register the nodes at port `8001` and `8002` with the already running `8000`.

```sh
curl -X POST \
  http://127.0.0.1:8001/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8000"}'
```

```sh
curl -X POST \
  http://127.0.0.1:8002/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8000"}'
```

This will make the node at port 8000 aware of the nodes at port 8001 and 8002, and make the newer nodes sync the chain with the node 8000, so that they are able to actively participate in the mining process post registration.

To update the node with which the frontend application syncs (default is localhost port 8000), change `CONNECTED_NODE_ADDRESS` field in the [views.py](/app/views.py) file.

Once you do all this, you can run the application, create transactions (post messages via the web inteface), and once you mine the transactions, all the nodes in the network will update the chain. The chain of the nodes can also be inspected by inovking `/chain` endpoint using cURL.

```sh
$ curl -X GET http://localhost:8001/chain
$ curl -X GET http://localhost:8002/chain
```

## Terminology

Node: A computer that operates on the blockchain network which is able to send and receive transactions.

Full node: A client that operates on the network and maintains a full copy of the blockchain. Sends and receives TX as well, updates the blockchain with block entries and confirmations from miners.

Master nodes: Master nodes enable decentralized governance and budgeting. In summary, aside from a full copy of the blockchain, a node also keeps additional data structures, such as the unspent transaction outputs cache or the unconfirmed transactions’ memory pool, so it can quickly validate new received transactions and mined blocks. If the received transaction or block is valid, the master node updates its data structures and relays it to the connected nodes. It is important to note that a master node does not need to trust other nodes because it independently validates all the information it receives from them.

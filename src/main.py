from blockchain import Blockchain
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

blockchain = Blockchain()
node_address = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'localhost')).replace('-', '')
app = Flask(__name__)
app.json.sort_keys = False
app.config['HOST'] = os.getenv('HOST', '0.0.0.0')
app.config['PORT'] = int(os.getenv('PORT', 8000))
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
app.config['HOSTNAME'] = os.getenv('HOSTNAME', 'sastaHost')


@app.route('/')
def index():
    return jsonify(f"This is not a Blockchain application provided by {app.config['HOSTNAME']}")

@app.route('/mine', methods = ['GET'])
def mine():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    
    #TODO

    # previous_hash = previous_block['hash']
    previous_hash = blockchain.hash(previous_block)
    
    new_proof, proof_hash = blockchain.proof_of_work(previous_proof)  
    blockchain.add_transaction(node_address, app.config['HOSTNAME'], amount=0.69)
    new_block = blockchain.create_block(new_proof, previous_hash=previous_hash)
    response = {
        'message': "Congratulations, you have mined a new block",
        "proof_hash": proof_hash,
        **new_block,
    }
    return response, 200

@app.route('/chain', methods = ['GET'])
def chain():
    return {
        'chain': blockchain.chain, 
        'length': len(blockchain.chain)
    }, 200

@app.route('/validate', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)   
    
    if is_valid:
        response = { "message": "The blockchain is valid" } 
    else:
        response = { "message": "The blockchain is invalid" }
        
    return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    
    #check if all keys are available in json
    if not all (key in json for key in transaction_keys):
        return "some part of transactions missing", 400
    index = blockchain.add_transaction(sender=json['sender'], receiver=json['receiver'], amount=json['amount'])
    response = {'message': f'This transaction will be added to the block {index}'}
    return response, 201

@app.route('/connect_nodes', methods = ['POST'])
def connect_nodes():
    json = request.get_json()
    nodes = json['nodes']
    if nodes is None:
        return "No nodes configured", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        'message': 'New nodes connected successfully',
        'nodes': nodes
    }
    return response, 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        message = "The chain is replaced by the largest chain."
    else:
        message = "The current chain is the longest one."
    
    response = {
        'message': message,
        'chain': blockchain.chain
    }   
    return response, 200

if __name__ == '__main__':
    app.run(
        host = app.config['HOST'],
        port = app.config['PORT'], 
        debug = app.config['DEBUG']
        )
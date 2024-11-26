from datetime import datetime
import json
import hashlib
import requests
from urllib.parse import urlparse


class Blockchain:
    LEADING_ZEROS_COUNT = 4
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.create_block(proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain)+1,
            'timestamp': str(datetime.now()),
            'previous_hash': previous_hash,
            'proof': proof, 
            'transactions': self.transactions
        }
        
        #TODO
        # block["hash"] = self.hash(block)
        
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def get_proof(self, current_proof, previous_proof):
        return str(current_proof**2 - previous_proof**2)
    
    def proof_of_work(self, previous_proof):
        proof = 1
        #till you get the valid proof, increment the number, else 
        while True:
            hash_op = hashlib.sha256(
                    self.get_proof(current_proof = proof, previous_proof = previous_proof).encode()
                ).hexdigest()
            if hash_op[:self.LEADING_ZEROS_COUNT] == '0'*self.LEADING_ZEROS_COUNT:
                return proof, hash_op
            proof += 1       
    
    def hash(self, block):
        json_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(json_block).hexdigest()
    
    def is_chain_valid(self, chain):
        # loop through all elements of chain, check if previous hash matches with the current block previous hash 
        current_block_index = 1
        
        while current_block_index < len(chain):
            current_block = chain[current_block_index]
            previous_block = chain[current_block_index-1]

            #compare previous_hash of current block with hash of previous block
            #TODO
            if current_block['previous_hash'] != self.hash(previous_block):
                return False
            
            #check if problem is actually solved by recalculating new hash and checking the limiting condition
            previous_proof = previous_block['proof']
            current_proof = current_block['proof']
            hash_operation = hashlib.sha256(
                self.get_proof( 
                          current_proof = current_proof, 
                          previous_proof = previous_proof
                        ).encode()
            ).hexdigest()
            if hash_operation[:self.LEADING_ZEROS_COUNT] != '0'*self.LEADING_ZEROS_COUNT:
                return False
            current_block_index += 1
        
        return True
        
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append(
            {
                'sender': sender,
                'receiver': receiver,
                'amount': amount  
            }
        )
        
        previous_block = self.get_previous_block()
        transaction_block_index = previous_block['index'] + 1
        return transaction_block_index
            
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) 
        return self.nodes
    
    def replace_chain(self):
        nodes = self.nodes
        max_length = len(self.chain)
        longest_chain = None
        print(nodes)
        
        for node in nodes:
            response = requests.get(f"http://{node}/chain")
            
            if response.status_code == 200:
                chain = response.json()['chain']
                length = response.json()['length']
                print("response 200")
                print(node)
                print(chain)
                print(length)
            
                if length > max_length and self.is_chain_valid(chain):
                    longest_chain = chain
                    max_length = length
                    
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
                                           

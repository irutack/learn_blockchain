import hashlib
import json
import requests
from textwrap import dedent
from time import time
from urllib.parse import urlparse
from uuid import uuid4

from flask import Flask, jsonify, request

class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        #  ジェネシスブロックを作る
        self.new_block(proof=100, previous_hash=1)


    def new_block(self, proof, previous_hash=None):
        
        """
        :param previous_hash: (Optional) <str> 1つ前のブロックのhash
        :param proof: <int> PoW

        :return: <dict> 新たなBlock
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []

        self.chain.append(block)
        return block


    def new_transaction(self, sender, recipient, amount):
        """
        :param sender: <str> 送信者アドレス
        :param recipient: <str> 受信者アドレス
        :param amount: <int>

        :return: <int> 次のBlockに使われるindex
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1


    def register_node(self, address):
        """
        :param address: <str> ほかのネットワークノードのアドレス
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


    def valid_chain(self, chain):
        """
        チェーンの妥当性検証
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
        
        return True


    def resolve_conflicts(self):
        """
        より長い妥当なチェーンに置き換える
        """
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
            
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        
        return False


    @staticmethod
    def hash(block):
        """
        :param block: <dict> hash化対象Block 
        :return: <str>
        """

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        return self.chain[-1]


    def proof_of_work(self, last_proof):
        """
        PoWの単純な例
        最新のproof(last_proof)に対して
        計算を行った結果が特定の条件となるようなある値(proof)を探す

        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        
        return proof


    @staticmethod
    def valid_proof(last_proof, proof):
        """
        上記'特定の条件'の計算部分
        """ 

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-','')
blockchain = BlockChain()


#  それまでの取引記録を新たなブロックとして追加する
@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    
    response = {
        'message': "New Block",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


#  取引内容
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return "Missing value", 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


#  ブロックの全体を見る
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
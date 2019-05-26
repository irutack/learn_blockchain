import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # ジェネシスブロックを作る
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

        :return: <int> 次のマイニングで用いられるindex
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

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

@app.route('/mine', method=['GET'])
def mine():
    return "mine!"

@app.route('/transactions/new', method=['POST'])
def new_transaction():
    return "new tran"

@app.route('/chain', method=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
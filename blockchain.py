import hashlib
import json
from time import time

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
        pass

tmp = BlockChain()
tmp.new_transaction(sender='alice',recipient='bob',amount=100)

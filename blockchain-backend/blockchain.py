import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json
import os
import base64
import time
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SECRET_KEY = b'16byteslongkey!!'
BLOCKCHAIN_FILE = "blockchain.json"

def encrypt_data(data):
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv=SECRET_KEY[:16])
    encrypted_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + encrypted_bytes).decode()

def decrypt_data(encrypted_data):
    try:
        raw_data = base64.b64decode(encrypted_data)
        iv = raw_data[:16]
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        decrypted_bytes = unpad(cipher.decrypt(raw_data[16:]), AES.block_size)
        return decrypted_bytes.decode()
    except:
        print("[ERROR] Blockchain file is corrupted or unreadable!")
        return None

def save_blockchain(blockchain, filename):
    encrypted_data = encrypt_data(json.dumps(blockchain, indent=4))
    os.chmod(filename, 0o666)
    with open(filename, "w") as file:
        file.write(encrypted_data)
    os.chmod(filename, 0o444)

def load_blockchain(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as file:
        encrypted_data = file.read()
    decrypted_data = decrypt_data(encrypted_data)
    return json.loads(decrypted_data) if decrypted_data else []

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_content = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_content.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

class Blockchain:
    def __init__(self):
        if not os.path.exists(BLOCKCHAIN_FILE):
            open(BLOCKCHAIN_FILE, 'w').close()

        self.chain = load_blockchain(BLOCKCHAIN_FILE)
        if not self.chain:
            print("[INFO] Creating new blockchain...")
            self.chain = [self.create_genesis_block().to_dict()]
            self.save_blockchain()
        else:
            print("[INFO] Blockchain loaded successfully!")

    def create_genesis_block(self):
        return Block(0, time.strftime("%y-%m-%d %H:%M:%S"), "Genesis Block", "0")

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(
            len(self.chain),
            time.strftime("%y-%m-%d %H:%M:%S"),
            data,
            previous_block["hash"]
        )
        self.chain.append(new_block.to_dict())
        self.save_blockchain()

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            recomputed_hash = hashlib.sha256(
                f"{current_block['index']}{current_block['timestamp']}{current_block['data']}{current_block['previous_hash']}".encode()
            ).hexdigest()

            if current_block["hash"] != recomputed_hash:
                print(f"[ERROR] Block {i} has been modified!")
                return False
            if current_block["previous_hash"] != previous_block["hash"]:
                print(f"[ERROR] Block {i} is linked to an incorrect previous block!")
                return False
        print("[SUCCESS] Blockchain is valid!")
        return True

    def save_blockchain(self):
        save_blockchain(self.chain, BLOCKCHAIN_FILE)

# 🔁 Instantiate blockchain
my_blockchain = Blockchain()

# ✅ Flask Routes
@app.route("/")
def home():
    return "✅ Blockchain Backend Running"

@app.route("/add", methods=["POST"])
def add_transaction():
    data = request.get_json()
    details = data.get("details")
    phone = data.get("phone_number")

    if not details or not phone:
        return jsonify({"error": "Missing fields"}), 400

    new_data = {
        "details": details,
        "phone_number": phone
    }
    my_blockchain.add_block(new_data)
    return jsonify({"message": "Transaction added successfully"}), 200

@app.route("/view", methods=["GET"])
def view_blockchain():
    return jsonify(my_blockchain.chain), 200

@app.route("/validate", methods=["GET"])
def validate_chain():
    return jsonify({"valid": my_blockchain.is_chain_valid()}), 200

# 🏁 Run server
if __name__ == "__main__":
    app.run(debug=True, port=5000)

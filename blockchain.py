import random
import time
import json
import os
import hashlib
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from pymongo import MongoClient
from datetime import datetime, timedelta
from pymongo import DESCENDING

# Flask App
app = Flask(__name__)
CORS(app)

# Constants
SECRET_KEY = b'16byteslongkey!!'
BLOCKCHAIN_FILE = "blockchain.json"
otp_store = {}  # Stores OTPs temporarily for verification
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "blockchainDB"
COLLECTION_NAME = "archives"

# MongoDB Setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# 🔐 AES Encryption
def encrypt_data(data):
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv=SECRET_KEY[:16])
    encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + encrypted).decode()

def decrypt_data(encrypted_data):
    try:
        raw = base64.b64decode(encrypted_data)
        iv = raw[:16]
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(raw[16:]), AES.block_size)
        return decrypted.decode()
    except Exception as e:
        print("[ERROR] Decryption failed:", str(e))
        return None

# 📁 Blockchain File Operations
def save_blockchain(blockchain, filename):
    encrypted = encrypt_data(json.dumps(blockchain, indent=4))
    os.chmod(filename, 0o666)
    with open(filename, "w") as f:
        f.write(encrypted)
    os.chmod(filename, 0o444)

def load_blockchain(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        encrypted = f.read()
    decrypted = decrypt_data(encrypted)
    return json.loads(decrypted) if decrypted else []

# 🧊 Archive Old Blockchain File
def archive_old_file_if_needed():
    if not os.path.exists(BLOCKCHAIN_FILE):
        return

    created_timestamp = datetime.fromtimestamp(os.path.getctime(BLOCKCHAIN_FILE))
    if datetime.now() - created_timestamp > timedelta(days=30):
        with open(BLOCKCHAIN_FILE, "rb") as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode()
            collection.insert_one({
                "file_name": f"archived_{int(time.time())}.json",
                "content_base64": encoded,
                "archived_at": datetime.now()
                "month": datetime.now().strftime("%Y-%m")
            })
        os.remove(BLOCKCHAIN_FILE)
        open(BLOCKCHAIN_FILE, 'w').close()
def restore_from_latest_archive():
    try:
        # Connect to MongoDB
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Get the latest archive (sorted by timestamp descending)
        latest_archive = collection.find_one(sort=[("timestamp", DESCENDING)])
        if latest_archive:
            encrypted_data = base64.b64decode(latest_archive["data"])
            with open(BLOCKCHAIN_FILE, "wb") as file:
                file.write(encrypted_data)
            print("[INFO] Blockchain restored from latest archive.")
            return True
        else:
            print("[WARN] No archive found in MongoDB.")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to restore from archive: {e}")
        return False

# ⛓️ Block & Blockchain Classes
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        content = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        archive_old_file_if_needed()  # 🆕 Archive logic added

        if not os.path.exists(BLOCKCHAIN_FILE):
            open(BLOCKCHAIN_FILE, 'w').close()

        self.chain = load_blockchain(BLOCKCHAIN_FILE)
        if not self.chain:
            print("[INFO] No blockchain found. Creating new one.")
            self.chain = [self.create_genesis_block().to_dict()]
            self.save_blockchain()
        else:
            print("[INFO] Blockchain loaded successfully.")

    def create_genesis_block(self):
        return Block(0, time.strftime("%Y-%m-%d %H:%M:%S"), "Genesis Block", "0")

    def add_block(self, data):
        prev = self.chain[-1]
        new_block = Block(len(self.chain), time.strftime("%Y-%m-%d %H:%M:%S"), data, prev["hash"])
        self.chain.append(new_block.to_dict())
        self.save_blockchain()

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            recomputed = hashlib.sha256(f"{curr['index']}{curr['timestamp']}{curr['data']}{curr['previous_hash']}".encode()).hexdigest()
            if curr["hash"] != recomputed:
                print(f"[ERROR] Block {i} has been tampered!")
                return False
            if curr["previous_hash"] != prev["hash"]:
                print(f"[ERROR] Block {i} is incorrectly linked!")
                return False
        return True

    def save_blockchain(self):
        save_blockchain(self.chain, BLOCKCHAIN_FILE)

# 🔁 Initialize Blockchain
my_blockchain = Blockchain()

# 🧩 OTP Simulation
def generate_otp():
    return str(random.randint(100000, 999999))

# 📦 Flask Routes
@app.route("/")
def home():
    return "✅ Blockchain Backend Running"

@app.route("/send_otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    phone = data.get("phone_number")

    if not phone:
        return jsonify({"error": "Phone number required"}), 400

    otp = generate_otp()
    otp_store[phone] = otp
    print(f"[DEBUG] OTP for {phone} is {otp}")
    return jsonify({"message": f"OTP sent to {phone} (simulated)."}), 200

@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    phone = data.get("phone_number")
    entered_otp = data.get("otp")

    if otp_store.get(phone) == entered_otp:
        del otp_store[phone]
        return jsonify({"verified": True}), 200
    return jsonify({"verified": False, "error": "Invalid OTP"}), 400

@app.route("/add", methods=["POST"])
def add_transaction():
    data = request.get_json()
    details = data.get("details")
    phone = data.get("phone_number")

    if not details or not phone:
        return jsonify({"error": "Missing details or phone number"}), 400

    new_data = {
        "details": details,
        "phone_number": phone
    }
    my_blockchain.add_block(new_data)
    return jsonify({"message": "✅ Transaction added"}), 200

@app.route("/view", methods=["GET"])
def view_chain():
    return jsonify(my_blockchain.chain), 200

@app.route("/validate", methods=["GET"])
def validate_chain():
    valid = my_blockchain.is_chain_valid()
    return jsonify({"valid": valid}), 200

# 🏁 Run Server
if __name__ == "__main__":
    app.run(debug=True, port=5000)

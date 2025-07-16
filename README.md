# PyCharmVault
centralized OTP verified blockchain ledger
# 🔐 PyCharmVault – OTP-Verified Blockchain System

A secure and centralized blockchain ledger system built with **Flask** and **React**, featuring:
- OTP-based transaction verification
- AES-encrypted blockchain file
- MongoDB backup & monthly archiving
- Integrity validation with self-healing restore

---

## 🚀 Features

- ✅ Add transaction blocks with phone + OTP simulation
- 🔒 AES-encryption for blockchain JSON files
- 🧩 Monthly archival in MongoDB for older blocks
- 🔄 Auto-restore from backup if tampered
- 🌐 Modern React.js frontend with transaction & chain viewer

---

## 🛠️ Tech Stack

| Layer      | Technology |
|------------|------------|
| Frontend   | React.js, HTML/CSS |
| Backend    | Python Flask |
| Database   | MongoDB |
| Security   | AES Encryption |
| Others     | Git, REST API, JSON |

---

## 🧪 How to Run Locally

### 🖥️ Backend (Flask)
```bash
cd blockchain-backend
pip install -r requirements.txt
python blockchain.py

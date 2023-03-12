import hashlib
import time
from cryptography.fernet import Fernet

ACCOUNT_FILE = "account.txt"
BALANCE_FILE = "balance.txt"
KEY_FILE = "key.key"
DEFAULT_BALANCE = 0


def load_account():
    try:
        with open(ACCOUNT_FILE, "r") as f:
            account_name = f.read().strip()
    except FileNotFoundError:
        print("Error: Account file not found.")
        exit(1)
    return account_name


def load_balance():
    try:
        with open(BALANCE_FILE, "rb") as f:
            data = f.read()
            fernet = Fernet(load_key())
            balance = int(fernet.decrypt(data).decode())
    except FileNotFoundError:
        balance = DEFAULT_BALANCE
        with open(BALANCE_FILE, "wb") as f:
            fernet = Fernet(generate_key())
            encrypted_data = fernet.encrypt(str(balance).encode())
            f.write(encrypted_data)
    return balance


def update_balance(balance):
    with open(BALANCE_FILE, "wb") as f:
        fernet = Fernet(load_key())
        encrypted_data = fernet.encrypt(str(balance).encode())
        f.write(encrypted_data)


def check_balance():
    balance = load_balance()
    print(f"Your current balance is: {balance}")


def create_hashcash():
    amount = int(input("Enter the amount: "))
    receiver = input("Enter the receiver address: ")

    balance = load_balance()
    if balance < amount:
        print("Insufficient balance.")
        return

    timestamp = int(time.time() + 60)  # expires in 1 minute
    message = f"{amount}:{receiver}:{timestamp}"

    nonce = 0
    while True:
        candidate = f"{message}:{nonce}".encode("utf-8")
        hashcash = hashlib.sha1(candidate).hexdigest()
        if hashcash.startswith("00000"):
            print(f"Cash, this is what you send to the reciver: {candidate}")
            print(f"Hash, Proof the transaction is valid: {hashcash}")
            update_balance(balance - amount)
            break
        nonce += 1


def receive_hashcash():
    account_name = load_account()
    candidate = input("Enter the hashcash candidate: ")
    try:
        amount, receiver, timestamp, nonce = candidate.split(":")
        amount = int(amount)
        timestamp = int(timestamp)
        nonce = int(nonce)
    except ValueError:
        print("Error: Invalid candidate format.")
        return

    balance = load_balance()
    if balance < amount:
        print("Error: Insufficient balance.")
        return

    current_time = int(time.time())
    if timestamp <= current_time:
        print("Error: Candidate has expired.")
        return

    message = f"{amount}:{receiver}:{timestamp}"
    candidate_str = f"{message}:{nonce}"
    hashcash = hashlib.sha1(candidate_str.encode()).hexdigest()
    if hashcash[:5] != "00000":
        print("Error: Invalid hashcash candidate.")
        return

    if receiver != account_name:
        print("Error: Candidate is not for this account.")
        return

    print(f"Cash candidate verified: {candidate_str}")
    update_balance(balance + amount)
    print(f"Amount {amount} added to your account balance.")


def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def load_key():
    with open(KEY_FILE, "rb") as f:
        key = f.read()
    return key


print("""\033[91mi\033[0m\033[94mf\033[0m\033[92mx \033[0mHashPay v0.1
 ██████╗██████╗ ███████╗██████╗ ███████╗████████╗██╗██╗  ██╗███████╗
██╔════╝██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝██║██║ ██╔╝██╔════╝
██║     ██████╔╝█████╗  ██║  ██║███████╗   ██║   ██║█████╔╝ ███████╗
██║     ██╔══██╗██╔══╝  ██║  ██║╚════██║   ██║   ██║██╔═██╗ ╚════██║
╚██████╗██║  ██║███████╗██████╔╝███████║   ██║   ██║██║  ██╗███████║
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝
                                                               v0.1                                
""")
while True:
  print("Choose an option:\n1. Check balance\n2. Make a transaction\n3. Receive Cash\n4. Exit")
  choice = input("X-HashPay > ")
  if choice == "1":
    check_balance()
  elif choice == "2":
    create_hashcash()
  elif choice == "3":
    receive_hashcash()
  elif choice == "4":
    break
  else:
    print("Invalid choice.")

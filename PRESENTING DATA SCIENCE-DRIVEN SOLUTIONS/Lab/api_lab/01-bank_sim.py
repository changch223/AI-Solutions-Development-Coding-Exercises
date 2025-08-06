from pydantic import BaseModel, Field, ValidationError
from typing import Dict

# In-memory account storage
accounts_db: Dict[str, float] = {}

# Data models
class AccountCreate(BaseModel):
    username: str = Field(..., min_length=3)
    initial_deposit: float = Field(..., gt=0)

class Transaction(BaseModel):
    username: str
    amount: float = Field(..., gt=0)

# Bank logic
def create_account(data: dict):
    try:
        account = AccountCreate(**data)
        if account.username in accounts_db:
            print(f" Account '{account.username}' already exists.")
        else:
            accounts_db[account.username] = account.initial_deposit
            print(f" Account created for {account.username} with balance ${account.initial_deposit:.2f}")
    except ValidationError as e:
        print(" Validation error:", e)

def deposit(data: dict):
    try:
        transaction = Transaction(**data)
        if transaction.username not in accounts_db:
            print(" Account not found.")
        else:
            accounts_db[transaction.username] += transaction.amount
            print(f"Deposited ${transaction.amount:.2f}. New balance: ${accounts_db[transaction.username]:.2f}")
    except ValidationError as e:
        print(" Validation error:", e)

def withdraw(data: dict):
    try:
        transaction = Transaction(**data)
        if transaction.username not in accounts_db:
            print(" Account not found.")
        elif accounts_db[transaction.username] < transaction.amount:
            print(" Insufficient funds.")
        else:
            accounts_db[transaction.username] -= transaction.amount
            print(f" Withdrawn ${transaction.amount:.2f}. New balance: ${accounts_db[transaction.username]:.2f}")
    except ValidationError as e:
        print(" Validation error:", e)

def check_balance(username: str):
    if username in accounts_db:
        print(f"{username}'s balance: ${accounts_db[username]:.2f}")
    else:
        print(" Account not found.")

# --- Example Usage ---
if __name__ == "__main__":
    create_account({"username": "alice", "initial_deposit": 1000})
    deposit({"username": "alice", "amount": 250})
    withdraw({"username": "alice", "amount": 100})
    check_balance("alice")

    print("\n-- Trying edge cases --\n")
    create_account({"username": "al", "initial_deposit": -50})  # Fail: username too short & deposit invalid
    withdraw({"username": "bob", "amount": 50})                # Fail: account not found
    deposit({"username": "alice", "amount": -10})              # Fail: invalid deposit

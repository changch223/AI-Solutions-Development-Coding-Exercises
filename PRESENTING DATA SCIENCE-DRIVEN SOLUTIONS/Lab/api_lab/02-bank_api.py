from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict

app = FastAPI()

# In-memory "database"
accounts_db: Dict[str, float] = {}

# Pydantic models
class AccountCreate(BaseModel):
    username: str = Field(..., min_length=3)
    initial_deposit: float = Field(..., gt=0)

class Transaction(BaseModel):
    username: str
    amount: float = Field(..., gt=0)

# Create account
@app.post("/account/create")
def create_account(account: AccountCreate):
    if account.username in accounts_db:
        raise HTTPException(status_code=400, detail="Account already exists.")
    accounts_db[account.username] = account.initial_deposit
    return {"message": f"Account created for {account.username}", "balance": account.initial_deposit}

# Deposit money
@app.post("/account/deposit")
def deposit(transaction: Transaction):
    if transaction.username not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found.")
    accounts_db[transaction.username] += transaction.amount
    return {"message": "Deposit successful", "new_balance": accounts_db[transaction.username]}

# Withdraw money
@app.post("/account/withdraw")
def withdraw(transaction: Transaction):
    if transaction.username not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found.")
    if accounts_db[transaction.username] < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds.")
    accounts_db[transaction.username] -= transaction.amount
    return {"message": "Withdrawal successful", "new_balance": accounts_db[transaction.username]}

# Get balance
@app.get("/account/{username}")
def get_balance(username: str):
    if username not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found.")
    return {"username": username, "balance": accounts_db[username]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("02-bank_api:app", host="0.0.0.0", port=8000, reload=True)
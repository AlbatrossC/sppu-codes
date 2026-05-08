def deposit(balance, amount):
    return balance + amount

def withdraw(balance, amount):
    if balance >= amount:
        return balance - amount
    else:
        print("Withdrawal denied: Insufficient balance.")
        return balance

balance = 0

transaction_log = input("Enter transaction log (e.g., 'D 100, W 200'): ")
transactions = transaction_log.split(", ")

for transaction in transactions:
    action, amount = transaction.split()
    amount = int(amount)
    
    if action == 'D':
        balance = deposit(balance, amount)
    elif action == 'W':
        balance = withdraw(balance, amount)
    else:
        print(f"Invalid transaction type '{action}'. Use 'D' for deposit or 'W' for withdrawal.")

print("Total Balance:", balance)

from pysondb import db
from operations import Operations

eur_pln = float(input("Price of 1 EUR (in PLN): "))
usd_pln = float(input("Price of 1 USD (in PLN): "))
usd_eur = float(input("Price of 1 USD (in EUR): "))

commission = float(input("Commission rate (in %): ")) / 100

users_db = db.getDb("users.json")
username = input("Enter your username: ").lower()

uid = 0
data = users_db.getByQuery({"name": username})
if data:
    data = data[0]
    password = input("Enter your password: ")
    if password == data["password"]:
        uid = data["id"]
        print("Verified successfully.")
    else:
        print("Incorrect password.")
        quit()
else:
    new_account_decision = input("No account found. Would you like to create one? (yes/no) ").lower()
    if new_account_decision == "yes":
        password = input("Enter password: ")
        user = {"name": username, "password": password, "pln": 0, "eur": 0, "usd": 0, "history": []}
        new_user_id = users_db.add(user)
        if new_user_id:
            data = users_db.getByQuery({"name": username})
            uid = new_user_id
            print("Account created.")
    else:
        quit()

operations = Operations(username, data, eur_pln, usd_pln, usd_eur, commission)


def choose_account(user_id):
    account_type_selected = input("Select account (pln/eur/usd) or quit (q): ")
    if account_type_selected.lower() == "q":
        return False
    elif account_type_selected == "pln" or account_type_selected == "eur" or account_type_selected == "usd":
        operations.operate(user_id, account_type_selected)
    else:
        print("Incorrect value.")
    return True


while choose_account(uid):
    data = users_db.getByQuery({"name": username})
    choose_account(uid)

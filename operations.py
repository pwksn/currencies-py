from pysondb import db

from history import History
from validators import Validators


class Operations:

    def __init__(self, username, data, eur_pln, usd_pln, usd_eur, commission):
        self.eur_pln = eur_pln
        self.usd_pln = usd_pln
        self.usd_eur = usd_eur
        self.commission = commission
        self.users_db = db.getDb("users.json")
        self.data = data
        self.validators = Validators()
        self.history = History(self.data, self.users_db)

    def operate(self, user_id, account_type):
        operation_id = input("""
        Select operation:
        (1) Deposit
        (2) Withdrawal 
        (3) Transfer
        (4) Currency exchange 
        (5) History
        (6) Account details
        (7) Profits
        (Q) Quit
            """)
        if operation_id == "1":
            self.deposit(user_id, account_type)
        elif operation_id == "2":
            self.withdraw(user_id, account_type)
        elif operation_id == "3":
            self.transfer(user_id, account_type)
        elif operation_id == "4":
            self.exchange(user_id)
        elif operation_id == "5":
            self.history.display_history(user_id)
        elif operation_id == "6":
            self.history.display_account_details(user_id, account_type)
        elif operation_id == "7":
            self.history.display_profit(user_id)
        elif operation_id.lower() == "q":
            print(123)
            return
        else:
            print("Invalid operation.")

    def deposit(self, user_id, account_type):
        amount = input(f"Deposit (in {account_type.upper()}): ")
        if not self.validators.is_value_correct(amount):
            print("Incorrect value.")
            return
        amount = float(amount)
        user_data = self.users_db.getById(int(user_id))
        self.users_db.updateById(user_id, {account_type: user_data[account_type] + amount})
        self.history.update_history(user_id, account_type, "deposit", amount)
        self.get_commission(amount, user_id, account_type)
        print("Deposit completed.")

    def withdraw(self, user_id, account_type):
        balance = self.users_db.getById(int(user_id))[account_type]
        print(f"Your account balance is: {balance} {account_type.upper()}.")
        amount = input(f"Withdrawal (in {account_type.upper()}): ")
        if not self.validators.is_value_correct(amount):
            print("Incorrect value.")
            return
        amount = float(amount)
        if amount <= balance:
            rest = balance - amount
            self.users_db.updateById(user_id, {account_type: rest})
            self.history.update_history(user_id, account_type, "withdraw", amount)
            self.get_commission(amount, user_id, account_type)
        else:
            print("Your account balance is too low, sorry.")

    def transfer(self, user_id, account_type):
        user_selection = input("Would you like to find target user by ID or by username? (id/u)").lower()
        target_user = {}
        if user_selection == "id":
            target_user_id = int(input("Enter user ID: "))
            target_user = self.users_db.getById(int(target_user_id))
        elif user_selection == "u":
            target_user_name = input("Enter username: ")
            target_user = self.users_db.getByQuery({"name": target_user_name})
        else:
            print("Invalid option.")

        if not target_user:
            print("User not found.")
        else:
            target_user = target_user[0]
            amount = input(f"Amount to transfer (in {account_type.upper()}): ")
            if not self.validators.is_value_correct(amount):
                print("Incorrect value.")
                return
            amount = float(amount)
            balance = self.users_db.getById(int(user_id))[account_type]
            if amount <= balance:
                rest = balance - amount
                self.users_db.updateById(int(user_id), {account_type: rest})
                self.users_db.updateById(int(target_user["id"]), {account_type: target_user[account_type] + amount})
                self.history.update_history(user_id, account_type, "transfer_out", amount)
                self.history.update_history(int(target_user["id"]), account_type, "transfer_in", amount)
                self.get_commission(amount, user_id, account_type)
                print("Money transferred.")
            else:
                print("Your account balance is too low, sorry.")

    def exchange(self, user_id):
        user_data = self.users_db.getById(int(user_id))
        print(
            f"Your accounts balance: {user_data['pln']} PLN, {user_data['eur']} EUR, {user_data['usd']} USD.")
        currency_sell = input("Which currency do you want to sell? (pln/eur/usd) ").lower()
        currency_buy = input("Which currency do you want to buy? (pln/eur/usd) ").lower()
        if currency_sell == currency_buy:
            print("You entered the same currency.")
            return
        buy_amount = input(f"How many {currency_buy.upper()} do you want to buy? ")
        if not self.validators.is_value_correct(buy_amount):
            print("Incorrect value.")
            return
        buy_amount = float(buy_amount)
        if currency_sell == "pln" and currency_buy == "eur":
            price = buy_amount * self.eur_pln
        elif currency_sell == "pln" and currency_buy == "usd":
            price = buy_amount * self.usd_pln
        elif currency_sell == "usd" and currency_buy == "eur":
            price = buy_amount * self.usd_eur
        elif currency_sell == "eur" and currency_buy == "pln":
            price = buy_amount * (1 / self.eur_pln)
        elif currency_sell == "usd" and currency_buy == "pln":
            price = buy_amount * (1 / self.usd_pln)
        elif currency_sell == "eur" and currency_buy == "usd":
            price = buy_amount * (1 / self.usd_eur)
        else:
            print("Error during processing data.")
        balance = self.data[currency_sell]
        if price <= balance:
            rest = balance - price
            self.users_db.updateById(int(user_id),
                                     {currency_sell: rest, currency_buy: self.data[currency_buy] + buy_amount})
            self.history.update_history(user_id, currency_sell, "exchange_sell", price)
            self.history.update_history(user_id, currency_buy, "exchange_buy", buy_amount)
            self.get_commission(price, user_id, currency_sell)
            print("Currencies exchanged.")
        else:
            print("Your account balance is too low, sorry.")

    def get_commission(self, amount, user_id, account_type):
        current_amount = self.users_db.getById(int(user_id))[account_type]
        self.users_db.updateById(user_id, {account_type: (current_amount - amount * self.commission)})

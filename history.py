from datetime import datetime


class History:

    def __init__(self, data, users_db):
        self.data = data
        self.users_db = users_db

    def update_history(self, user_id, account_type, operation, amount):
        account_history = self.users_db.getById(int(user_id))["history"]
        now = datetime.now()
        account_history.append(
            {"operation": operation, "account_type": account_type, "amount": amount, "date": now.strftime("%d.%m.%Y")})
        self.users_db.updateById(int(user_id), {"history": account_history})

    def display_history(self, user_id):
        history_type = input("Select filter: (1) Operation type, (2) Currency, (3) Date ")
        account_history = self.users_db.getById(int(user_id))["history"]
        if history_type == "1":
            operation_key = input(
                "Select operation type: (1) Deposit, (2) Withdrawal, (3) Transfer out, (4) Transfer in, (5) Currency exchange (sell), (6) Currency exchange (buy) ")
            operation_keys = {"1": "deposit", "2": "withdraw", "3": "transfer_out", "4": "transfer_in", "5": "exchange_sell",
                              "6": "exchange_buy"}
            history_filtered = [x for x in account_history if x["operation"] == operation_keys[operation_key]]
            if history_filtered:
                self.style_history_msg(history_filtered)
            else:
                print("No history found.")
        elif history_type == "2":
            currency_key = input("Select currency: (1) PLN, (2) EUR, (3) USD: ")
            currency_keys = {"1": "pln", "2": "eur", "3": "usd"}
            history_filtered = [x for x in account_history if x["account_type"] == currency_keys[currency_key]]
            if history_filtered:
                self.style_history_msg(history_filtered)
            else:
                print("No history found.")
        elif history_type == "3":
            date_from = input("From: (dd.mm.YYYY, e.g. 21.04.2022) ")
            date_to = input("To: (dd.mm.YYYY, e.g. 21.04.2022) ")
            history_filtered = [x for x in account_history if date_from <= x["date"] <= date_to]
            if history_filtered:
                self.style_history_msg(history_filtered)
            else:
                print("No history found.")

    def style_history_msg(self, history_filtered):
        for el in history_filtered:
            print(f"""
    Operation: {el["operation"]}
    Account type: {el["account_type"].upper()}
    Cash amount: {el["amount"]}
    Date: {el["date"]}
    """)

    def display_account_details(self, user_id, account_type):
        account_history = self.users_db.getById(int(user_id))["history"]
        balance = self.data[account_type]
        history_filtered = [x for x in account_history if x["account_type"] == account_type]
        print(f"Account balance: {balance} {account_type.upper()}.")
        print("Account history: ")
        self.style_history_msg(history_filtered)

    def display_profit(self, user_id):
        account_history = self.users_db.getById(int(user_id))["history"]
        profit_type = input("Select profit filter: (1) All, (2) Operation type, (3) Currency: ")
        history_filtered = []
        if profit_type == "1":
            history_filtered = [x for x in account_history if x["operation"] == "deposit" or x["operation"] == "exchange_buy"]
        elif profit_type == "2":
            operation_type = input("Select operation type: (1) Deposit, (2) Exchanged money (buy), (3) Transfer in ")
            operation_keys = {"1": "deposit", "2": "exchange_buy", "3": "transfer_in"}
            history_filtered = [x for x in account_history if x["operation"] == operation_keys[operation_type]]
        elif profit_type == "3":
            currency_key = input("Select currency: (1) PLN, (2) EUR, (3) USD ")
            currency_keys = {"1": "pln", "2": "eur", "3": "usd"}
            history_filtered = [x for x in account_history if x["account_type"] == currency_keys[currency_key] and (x["operation"] == "deposit" or x["operation"] == "exchange_buy")]

        profit = {"pln": 0, "eur": 0, "usd": 0}
        if history_filtered:
            for i in range(len(history_filtered)):
                profit[history_filtered[i]["account_type"]] += history_filtered[i]["amount"]
        else:
            print("No profit found.")

        if profit["pln"]:
            print(f"Profit: {profit['pln']} PLN.")
        if profit["eur"]:
            print(f"Profit: {profit['eur']} EUR.")
        if profit["usd"]:
            print(f"Profit: {profit['usd']} USD.")

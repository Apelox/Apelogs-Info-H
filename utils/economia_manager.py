import json
import os

class Manager:
    def __init__(self, path='data/economia.json'):
        self.path = path
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)

    def load_data(self):
        with open(self.path, 'r') as f:
            return json.load(f)

    def save_data(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=4)

    def get_balance(self, user_id):
        data = self.load_data()
        return data.get(str(user_id), 0)

    def set_balance(self, user_id, amount):
        data = self.load_data()
        data[str(user_id)] = amount
        self.save_data(data)

    def add_balance(self, user_id, amount):
        current = self.get_balance(user_id)
        self.set_balance(user_id, current + amount)

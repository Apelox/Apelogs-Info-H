import json
import os
from datetime import datetime, timezone

class Manager:
    def __init__(self, path='data/economia.json'):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            initial_data = {
                "global": {
                    "jackpot": 1000,
                    "investimento": {
                        "preco_por_cota": 100.0,
                        "ultima_atualizacao": datetime.now(timezone.utc).isoformat(),
                        "preco_cota_historico": []
                    }
                },
                "users": {}
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=4)

    def load_data(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                investimento_global = data.setdefault('global', {}).setdefault('investimento', {
                    "preco_por_cota": 100.0,
                    "ultima_atualizacao": datetime.now(timezone.utc).isoformat(),
                    "preco_cota_historico": []
                })
                investimento_global.setdefault('preco_cota_historico', [])
                data.setdefault('users', {})
                return data
            except json.JSONDecodeError:
                return {
                    "global": {
                        "jackpot": 1000,
                        "investimento": {
                            "preco_por_cota": 100.0,
                            "ultima_atualizacao": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    "users": {}
                }

    def save_data(self, data):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def get_user_data(self, user_id):
        user_id_str = str(user_id)
        data = self.load_data()
        
        default_user_data = {
            "balance": 0, 
            "bank": 0,
            "biography": "Use /setbio para definir uma biografia!",
            "investments": {
                "cotas": 0.0,
                "total_investido_acumulado": 0
            },
            "badges": [],
            "daily_timestamp": None, 
            "work_timestamp": None
        }
        
        user_data = data["users"].get(user_id_str, default_user_data)
        
        user_data.setdefault("bank", 0)
        user_data.setdefault("biography", "Use /setbio para definir uma biografia!")
        user_data.setdefault("investments", {
            "cotas": 0.0,
            "total_investido_acumulado": 0
        })
        user_data.setdefault("badges", [])
        
        return user_data

    def set_user_data(self, user_id, user_data):
        user_id_str = str(user_id)
        data = self.load_data()
        data["users"][user_id_str] = user_data
        self.save_data(data)

    def get_balance(self, user_id):
        user_data = self.get_user_data(user_id)
        return user_data.get("balance", 0)

    def add_balance(self, user_id, amount):
        user_data = self.get_user_data(user_id)
        user_data["balance"] = user_data.get("balance", 0) + amount
        self.set_user_data(user_id, user_data)
        
    def get_cooldown(self, user_id, command_name):
        user_data = self.get_user_data(user_id)
        timestamp_str = user_data.get(f"{command_name}_timestamp")
        
        if not timestamp_str:
            return None
        try:
            return datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            return None

    def update_cooldown(self, user_id, command_name):
        user_data = self.get_user_data(user_id)
        user_data[f"{command_name}_timestamp"] = datetime.now(timezone.utc).isoformat()
        self.set_user_data(user_id, user_data)
    
    def get_jackpot(self):
        data = self.load_data()
        return data.get("global", {}).get("jackpot", 1000)

    def update_jackpot(self, amount):
        data = self.load_data()
        current_jackpot = self.get_jackpot()
        jackpot_cap = 100000 
        
        if current_jackpot < jackpot_cap:
            data.setdefault("global", {})["jackpot"] = min(current_jackpot + amount, jackpot_cap)
        
        self.save_data(data)

    def set_jackpot(self, amount):
        data = self.load_data()
        data.setdefault("global", {})["jackpot"] = amount
        self.save_data(data)
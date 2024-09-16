import json
import os

CONFIG_FILE = 'config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            'username': '',
            'password': '',
            'token': '',
            'token_refresh_interval': 21600,  # 默认6小时（21600秒）
            'time': '9:00'
        }
        save_config(default_config)
        return default_config
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def update_token(new_token):
    config = load_config()
    config['token'] = new_token
    save_config(config)

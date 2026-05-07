import yaml
import os

class Config:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "..", "config.yaml")
        
        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)

    @property
    def telegram_token(self):
        return self._config["telegram"]["token"]

    @property
    def chat_id(self):
        return self._config["telegram"]["chat_id"]

    @property
    def threads(self):
        return self._config["settings"]["threads"]
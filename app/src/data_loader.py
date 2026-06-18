import json
from typing import List, Dict

class DataLoader:
    def __init__(self, filepath: str):
        with open(filepath, 'r') as f:
            self.scenarios = json.load(f)

    def get_all_scenarios(self) -> List[Dict]:
        return self.scenarios
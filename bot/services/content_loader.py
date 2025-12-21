import os
import json
from typing import Dict, List, Optional

import aiofiles
import random


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOTA_PATH = os.path.join(BASE_DIR, "data", "dota_heroes.json")
CR_PATH = os.path.join(BASE_DIR, "data", "clash_royale_cards.json")


class ContentLoader():
    def __init__(self):
        self._dota_heroes: List[str] = []
        self._cr_cards: List[str] = []
        self._is_loaded: bool = False
        
    async def load_content(self) -> None:
        if self._is_loaded:
            return
        
        try:
            async with aiofiles.open(DOTA_PATH, mode='r', encoding='utf-8') as f:
                data = json.loads(await f.read())
                self._dota_heroes = data.get('heroes', [])
            
            async with aiofiles.open(CR_PATH, mode='r', encoding='utf-8') as f:
                data = json.loads(await f.read())
                self._cr_cards = data.get('cards', [])

            self._is_loaded = True
            print(f"Content loaded: Dota Heroes={len(self._dota_heroes)}, CR Cards={len(self._cr_cards)}")
        except FileNotFoundError as e:
            print(f"ERROR: File not found at {e.filename}")
            
    def get_random_location(self, theme: str) -> Optional[str]:
        if not self._is_loaded:
            return None
        
        if theme == 'DOTA' and self._dota_heroes:
            return random.choice(self._dota_heroes)
        elif theme == 'CR' and self._cr_cards:
            return random.choice(self._cr_cards)
        
        return None
    

content_loader = ContentLoader()
import os
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv()

@dataclass
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN")

def load_config() -> Settings:
    settings = Settings()

    if not settings.bot_token:
        raise ValueError("BOT_TOKEN is not set in environment variables")
    
    return settings

config = load_config()
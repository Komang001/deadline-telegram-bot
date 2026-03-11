from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

print("DEBUG TOKEN:", BOT_TOKEN)
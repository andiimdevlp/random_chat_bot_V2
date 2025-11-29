import os
from pyrogram import Client
from dotenv import load_dotenv
from storage.parquet_store import ensure_layout
from utils.logger import log_event

from commands.start_commands import register_start_handlers
from commands.chat_commands import register_chat_handlers
from commands.block_commands import register_block_handlers
from commands.new_commands import register_new_handlers
from commands.pause_commands import register_pause_handlers
from commands.forward_commands import register_forward_handlers
from commands.ban_commands import register_ban_handlers

load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ensure_layout()

app = Client("random_chat_bot_parquet", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

register_start_handlers(app)
register_chat_handlers(app)
register_block_handlers(app)
register_new_handlers(app)
register_pause_handlers(app)
register_forward_handlers(app)
register_ban_handlers(app)

if __name__ == "__main__":
    log_event("info","bot.starting")
    app.run()

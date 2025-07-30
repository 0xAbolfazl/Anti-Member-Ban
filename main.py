import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from .env with validation
try:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    CHANNEL = os.getenv("CHANNEL")  # Can be username or ID string
    
    if not all([API_ID, API_HASH, BOT_TOKEN, ADMIN_ID, CHANNEL]):
        raise ValueError("Missing required environment variables")
except Exception as e:
    print(f"Configuration error: {e}")
    exit(1)

# Create Pyrogram client
app = Client(
    "channel_stats_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

async def get_channel_stats():
    try:
        # Get channel info
        chat = await app.get_chat(CHANNEL)
        if not chat:
            print("Error: Could not get channel info")
            return None, None
        
        # Get members count
        members = await app.get_chat_members_count(chat.id)
        
        # Get banned users count
        banned_count = 0
        async for _ in app.get_chat_members(chat.id, filter=ChatMembersFilter.BANNED):
            banned_count += 1
            
        return members, banned_count
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None, None

async def send_channel_stats():
    while True:
        members, banned_count = await get_channel_stats()
        
        if members is not None and banned_count is not None:
            message = (
                f"📊 Channel Stats Update:\n\n"
                f"👥 Members: {members}\n"
                f"🚫 Banned Users: {banned_count}"
            )
            
            try:
                await app.send_message(ADMIN_ID, message)
            except Exception as e:
                print(f"Error sending message: {e}")
        
        # Wait for 10 seconds before next update
        await asyncio.sleep(10)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("🤖 Channel Stats Bot is running!\n\n"
                          "I will send channel stats every 10 seconds to this chat.")
        # Start the stats sending loop
        asyncio.create_task(send_channel_stats())

if __name__ == "__main__":
    print("Bot starting...")
    try:
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
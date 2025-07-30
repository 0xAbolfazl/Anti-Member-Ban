import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMember
from pyrogram.enums import ChatMembersFilter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL = os.getenv("CHANNEL")  # Channel username or ID

app = Client("ban_monitor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Track already notified bans to avoid duplicates
reported_bans = set()

async def send_ban_notification(admin_id, banned_user_id):
    try:
        # Check if we've already reported this ban
        ban_key = f"{admin_id}:{banned_user_id}"
        if ban_key in reported_bans:
            return
            
        admin = await app.get_users(admin_id)
        banned_user = await app.get_users(banned_user_id)
        
        message = (
            "🚨 New Ban Detected\n\n"
            f"🛡️ Admin: {admin.mention} (ID: {admin.id})\n"
            f"👤 Banned User: {banned_user.mention} (ID: {banned_user.id})"
        )
        
        await app.send_message(ADMIN_ID, message)
        reported_bans.add(ban_key)  # Mark as reported
        
    except Exception as e:
        print(f"Notification error: {e}")

async def check_for_new_bans():
    try:
        async for member in app.get_chat_members(CHANNEL, filter=ChatMembersFilter.BANNED):
            if isinstance(member, ChatMember) and hasattr(member, 'restricted_by') and member.restricted_by:
                await send_ban_notification(member.restricted_by.id, member.user.id)
                
    except Exception as e:
        print(f"Ban check error: {e}")

async def ban_monitor_loop():
    while True:
        await check_for_new_bans()
        await asyncio.sleep(10)  # Check every 10 seconds

@app.on_message(filters.command("start") & filters.private)
async def start_bot(client: Client, message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("🛡️ Ban Monitor Activated\n\n"
                          "I will notify you about new bans in the channel.")
        asyncio.create_task(ban_monitor_loop())

if __name__ == "__main__":
    print("Starting ban monitoring bot...")
    app.run()
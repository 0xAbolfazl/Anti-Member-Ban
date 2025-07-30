import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMember
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL = os.getenv("CHANNEL")  # Channel username or ID

app = Client("channel_stats_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def send_ban_notification(admin_id, banned_user_id):
    try:
        admin = await app.get_users(admin_id)
        banned_user = await app.get_users(banned_user_id)
        
        message = (
            "🚨 New user banned!\n\n"
            f"🛡️ Admin who banned: {admin.mention}\n"
            f"🆔 Admin ID: {admin.id}\n\n"
            f"👤 Banned user: {banned_user.mention}\n"
            f"🆔 User ID: {banned_user.id}"
        )
        
        await app.send_message(ADMIN_ID, message)
    except Exception as e:
        print(f"Error sending notification: {e}")

async def check_bans():
    try:
        # Get all banned users
        banned_users = []
        async for member in app.get_chat_members(CHANNEL, filter=ChatMembersFilter.BANNED):
            if isinstance(member, ChatMember) and hasattr(member, 'restricted_by'):
                admin_id = member.restricted_by.id if member.restricted_by else "Unknown"
                banned_users.append((admin_id, member.user.id))
        
        # Process new bans
        for admin_id, user_id in banned_users:
            await send_ban_notification(admin_id, user_id)
            
    except Exception as e:
        print(f"Error checking bans: {e}")

async def get_channel_stats():
    try:
        chat = await app.get_chat(CHANNEL)
        members = await app.get_chat_members_count(chat.id)
        
        banned_count = 0
        async for _ in app.get_chat_members(chat.id, filter=ChatMembersFilter.BANNED):
            banned_count += 1
            
        return members, banned_count
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None, None

async def send_channel_stats():
    while True:
        # Check for new bans first
        await check_bans()
        
        # Send regular stats
        members, banned_count = await get_channel_stats()
        if members is not None and banned_count is not None:
            message = (
                f"📊 Channel Stats:\n\n"
                f"👥 Total Members: {members}\n"
                f"🚫 Banned Users: {banned_count}"
            )
            await app.send_message(ADMIN_ID, message)
        
        await asyncio.sleep(10)  # Check every 10 seconds

@app.on_message(filters.command("start") & filters.private)
async def start_bot(client: Client, message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("🤖 Channel Monitor Bot Activated!\n\n"
                          "I will now track all bans and send you regular stats.")
        asyncio.create_task(send_channel_stats())

if __name__ == "__main__":
    print("Starting monitoring bot...")
    app.run()
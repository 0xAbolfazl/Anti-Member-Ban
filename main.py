import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL = os.getenv("CHANNEL")

app = Client("channel_stats_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to track last known admins
last_known_admins = {}

async def update_admins_list():
    global last_known_admins
    try:
        chat = await app.get_chat(CHANNEL)
        admins = await app.get_chat_members(chat.id, filter=ChatMembersFilter.ADMINISTRATORS)
        last_known_admins = {admin.user.id: admin.user.first_name for admin in admins}
    except Exception as e:
        print(f"Error updating admin list: {e}")

async def send_admin_notification(banned_user_id):
    try:
        banned_user = await app.get_users(banned_user_id)
        
        message = (
            "🚨 A user was banned!\n\n"
            f"👤 Banned user: {banned_user.mention}\n"
            f"🆔 User ID: {banned_user.id}\n\n"
            "Note: Could not determine which admin performed the ban (bot limitation)"
        )
        
        await app.send_message(ADMIN_ID, message)
    except Exception as e:
        print(f"Error sending notification: {e}")

@app.on_chat_member_updated()
async def handle_ban_event(client: Client, chat_member: ChatMemberUpdated):
    try:
        # Check if this is our channel
        chat = await app.get_chat(CHANNEL)
        if chat_member.chat.id != chat.id:
            return
            
        # Check if user was banned
        if (chat_member.old_chat_member and chat_member.new_chat_member and
            chat_member.old_chat_member.status != ChatMemberStatus.BANNED and
            chat_member.new_chat_member.status == ChatMemberStatus.BANNED):
            
            # Update admin list
            await update_admins_list()
            
            # Send notification about the banned user
            await send_admin_notification(chat_member.new_chat_member.user.id)
            
    except Exception as e:
        print(f"Error handling ban event: {e}")

async def get_channel_stats():
    try:
        chat = await app.get_chat(CHANNEL)
        if not chat:
            print("Error: Could not get channel info")
            return None, None
        
        members = await app.get_chat_members_count(chat.id)
        
        banned_count = 0
        async for _ in app.get_chat_members(chat.id, filter=ChatMembersFilter.BANNED):
            banned_count += 1
            
        return members, banned_count
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None, None

async def send_channel_stats():
    # Initial admin list update
    await update_admins_list()
    
    while True:
        members, banned_count = await get_channel_stats()
        
        if members is not None and banned_count is not None:
            message = (
                f"📊 Channel Stats Update:\n\n"
                f"👥 Members: {members}\n"
                f"🚫 Banned Users: {banned_count}\n"
                f"🛡️ Admins Count: {len(last_known_admins)}"
            )
            
            try:
                await app.send_message(ADMIN_ID, message)
            except Exception as e:
                print(f"Error sending message: {e}")
        
        # Update admin list periodically
        if len(last_known_admins) == 0 or len(message) % 10 == 0:
            await update_admins_list()
        
        await asyncio.sleep(10)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("🤖 Channel Stats Bot is running!\n\n"
                          "I will send channel stats every 10 seconds to this chat.\n"
                          "I'll also notify you when users get banned.")
        asyncio.create_task(send_channel_stats())

if __name__ == "__main__":
    print("Bot starting...")
    try:
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
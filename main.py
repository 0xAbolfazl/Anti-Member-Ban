import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, ChatMember, ChatPrivileges
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL = os.getenv("CHANNEL")  # Channel username or ID

app = Client("ban_punish_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def enforce_rules(admin_id, banned_user_id):
    try:
        admin = await app.get_users(admin_id)
        banned_user = await app.get_users(banned_user_id)
        
        # Check if we have sufficient privileges to remove the admin
        me = await app.get_chat_member(CHANNEL, "me")
        if me.privileges and me.privileges.can_restrict_members:
            try:
                # Remove admin privileges first
                await app.promote_chat_member(
                    CHANNEL,
                    admin_id,
                    privileges=ChatPrivileges(
                        can_manage_chat=False,
                        can_delete_messages=False,
                        can_manage_video_chats=False,
                        can_restrict_members=False,
                        can_promote_members=False,
                        can_change_info=False,
                        can_post_messages=False,
                        can_edit_messages=False,
                        can_invite_users=False,
                        can_pin_messages=False
                    )
                )
                
                
                # Then ban and unban (remove from channel)
                await app.ban_chat_member(CHANNEL, admin_id)
                # await app.unban_chat_member(CHANNEL, admin_id)
                
                # Send detailed report
                report = (
                    "⚠️ Rule Violation Detected\n\n"
                    f"🛡️ Violating Admin: {admin.mention} (ID: {admin.id})\n"
                    f"👤 Banned Member: {banned_user.mention} (ID: {banned_user.id})\n\n"
                    "✅ Action Taken: Admin privileges revoked and removed from channel"
                )
            except Exception as e:
                report = (
                    "⚠️ Rule Violation Detected\n\n"
                    f"🛡️ Violating Admin: {admin.mention} (ID: {admin.id})\n"
                    f"👤 Banned Member: {banned_user.mention} (ID: {banned_user.id})\n\n"
                    f"❌ Failed to remove admin: {str(e)}"
                )
        else:
            report = (
                "⚠️ Rule Violation Detected\n\n"
                f"🛡️ Violating Admin: {admin.mention} (ID: {admin.id})\n"
                f"👤 Banned Member: {banned_user.mention} (ID: {banned_user.id})\n\n"
                "❌ Bot lacks sufficient privileges to remove this admin"
            )
        
        await app.send_message(ADMIN_ID, report)
        
    except Exception as e:
        print(f"Error processing violation: {e}")

async def monitor_bans():
    processed_violations = set()
    
    while True:
        try:
            async for member in app.get_chat_members(CHANNEL, filter=enums.ChatMembersFilter.BANNED):
                if (isinstance(member, ChatMember) and hasattr(member, 'restricted_by') and member.restricted_by):
                    violation_id = f"{member.restricted_by.id}-{member.user.id}"
                    
                    if violation_id not in processed_violations:
                        await enforce_rules(member.restricted_by.id, member.user.id)
                        processed_violations.add(violation_id)
                        
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        await asyncio.sleep(10)

@app.on_message(filters.command("start") & filters.private)
async def start_bot(client: Client, message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("🛡️ Ban Monitor & Enforcer Activated\n\n"
                          "I will:\n"
                          "1. Detect when admins ban members\n"
                          "2. Attempt to remove violating admins\n"
                          "3. Report all actions to you")
        
        # Verify bot privileges
        try:
            me = await app.get_chat_member(CHANNEL, "me")
            if not me.privileges or not me.privileges.can_restrict_members:
                await message.reply("⚠️ Warning: I don't have admin privileges to restrict members!")
        except Exception as e:
            await message.reply(f"⚠️ Error checking privileges: {str(e)}")
        
        asyncio.create_task(monitor_bans())

if __name__ == "__main__":
    print("Starting violation enforcement bot...")
    app.run()
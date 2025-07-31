# Telegram Ban Enforcement Bot

A Pyrogram-based bot that monitors and enforces channel ban policies by:

1. Detecting when admins ban members
2. Automatically removing violating admins
3. Reporting all actions to the main admin

## Features

- **Ban Monitoring**: Tracks all ban actions in the channel
- **Admin Enforcement**: Automatically removes admins who ban members
- **Detailed Reporting**: Sends violation reports to the main admin
- **Permission Checks**: Verifies bot privileges before acting

## Requirements

- Python 3.7+
- Pyrogram
- Telegram API credentials
- Bot with admin privileges in your channel

## Installation

1. Clone the repository or copy the bot code
2. Install dependencies:

    ```bash
    pip install pyrogram python-dotenv

3. Create a .env file with your credentials:

    ```env
    env
    API_ID=your_api_id
    API_HASH=your_api_hash
    BOT_TOKEN=your_bot_token
    ADMIN_ID=your_user_id
    CHANNEL=your_channel

## Configuration

Ensure your bot has these admin permissions:

1. Add admins
2. Change admin privileges
3. Delete messages (recommended)

## Usage

1. Start the bot with ```/start``` in your private chat
2. Add bot to your channel

- The bot will begin monitoring the channel
- Violations will be reported to your private chat

## Limitations

- Requires the bot to be admin with sufficient privileges
- Can only track bans made after bot activation

## Troubleshooting

If the bot fails to remove admins:

1. Verify the bot has all required permissions
2. Check that the bot's admin rank is higher than the admins it needs to remove

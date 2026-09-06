# Discord Bot 🤖

A feature-rich Discord bot built with discord.py featuring music playback, moderation, economy, and more.

## Features

### 🎵 Music Player
- Play songs from YouTube by search 
- Queue management with skip, pause, resume
- Now-playing display in channel topic
- Support for yt-dlp for robust video downloading

### 🛡️ Moderation
- Ban, kick, mute, and unmute members
- Warning system with persistent storage
- Message purge with optional user filtering
- Admin-only warn clearing

### 💰 Economy
- Currency system for users
- Customizable economy commands

### 🎉 Fun & Entertainment
- Fun commands for community engagement

### 📊 Logging
- Guild activity logging and tracking

### 👋 Welcome System
- Customizable welcome messages
- Member join notifications

## Requirements

- Python 3.8+
- FFmpeg (for audio playback)
- Discord.py 2.3.2+
- yt-dlp for YouTube integration

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lmao-create/discord-bot.git
   cd discord-bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Discord bot token
   ```

5. **Install FFmpeg** (required for music)
   - **Windows**: Download from https://ffmpeg.org/download.html or use `choco install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

## Running the Bot

```bash
python Bot.py
```

The bot will start and connect to Discord. All cogs will be loaded automatically from the `COGS` folder.

## Hosting Options

You can host this bot on various platforms:

### 1. **Local Machine**
- Simplest option for testing
- Requires your PC to stay on 24/7
- Works great for small communities
- No additional setup needed

### 2. **Heroku** (Free tier discontinued)
- ~~Previously free, now paid only~~
- Good for reliable uptime
- Easy deployment with git push

### 3. **Replit** (Recommended for beginners)
- Free tier available
- No credit card required
- Simple deployment
- Keep-alive options available
- Visit: https://replit.com

**Steps for Replit:**
1. Fork this repo to GitHub
2. Go to Replit.com and create new project
3. Import from GitHub
4. Add `.env` file with your TOKEN
5. Run `pip install -r requirements.txt`
6. Click Run to start the bot
7. Use UptimeRobot (free) to keep it alive

### 4. **PythonAnywhere**
- Free tier available
- Reliable hosting
- Good for 24/7 uptime
- Visit: https://www.pythonanywhere.com

**Steps for PythonAnywhere:**
1. Create account on PythonAnywhere
2. Upload bot files via web interface or git clone
3. Create a new web app (or console app)
4. Install requirements: `pip install -r requirements.txt`
5. Run in a bash console: `python Bot.py`
6. Use always-on feature for 24/7 uptime

### 5. **AWS, Google Cloud, Azure** (Paid)
- Professional hosting solutions
- Scalable and reliable
- More expensive but enterprise-grade
- Free tier available for new users

### 6. **VPS/Dedicated Server** (Paid)
- Full control over environment
- Better performance
- Providers: DigitalOcean, Linode, Vultr, etc.
- Typical cost: $5-20/month

**Steps for DigitalOcean Droplet:**
1. Create a droplet (Ubuntu 20.04+)
2. SSH into your server
3. Clone this repository
4. Install Python 3.8+: `sudo apt-get install python3 python3-pip`
5. Install FFmpeg: `sudo apt-get install ffmpeg`
6. Install requirements: `pip3 install -r requirements.txt`
7. Create `.env` file with your TOKEN
8. Run bot in background using `nohup` or `screen`

### 7. **Docker Container** (Advanced)
For containerized deployment on any platform.

**Create a `Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "Bot.py"]
```

**Build and run:**
```bash
docker build -t discord-bot .
docker run -d -e TOKEN=your_token discord-bot
```

### Recommendation
- **For testing**: Local machine or Replit
- **For small communities**: Replit or PythonAnywhere
- **For serious projects**: VPS (DigitalOcean) or Docker
- **For scaling**: AWS/Google Cloud/Azure

## Commands

### Music Commands
- `/play <song_name_or_url>` - Play a song from YouTube
- `/skip` - Skip to the next song
- `/stop` - Stop music and clear queue
- `/pause` - Pause the current song
- `/resume` - Resume paused song
- `/queue` - View the current music queue
- `/leave` - Disconnect from voice channel

### Moderation Commands
- `/ban <member> [reason]` - Ban a member
- `/kick <member> [reason]` - Kick a member
- `/mute <member> <duration>` - Mute a member (e.g., 1h, 30m)
- `/unmute <member> [reason]` - Unmute a member
- `/warn <member> [reason]` - Warn a member
- `/warns <member>` - View member's warnings
- `/clear_warns <member>` - Clear all warnings (admin only)
- `/unban <user> [reason]` - Unban a user
- `/purge <amount> [member]` - Delete messages

## Project Structure

```
discord-bot/
├── Bot.py              # Main bot entry point
├── COGS/               # Bot command modules
│   ├── Music.py        # Music player commands
│   ├── Moderation.py   # Moderation commands
│   ├── ECO.py          # Economy commands
│   ├── Fun.py          # Fun commands
│   ├── Logs.py         # Logging commands
│   └── Welcome.py      # Welcome system
├── .env.example        # Example environment file
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Configuration

### Environment Variables
Create a `.env` file in the root directory:
```
TOKEN=your_discord_bot_token
```

Get your bot token from the [Discord Developer Portal](https://discord.com/developers/applications).

### Data Files
The bot stores data in JSON files:
- `warns_data.json` - Warning records
- `economy_data.json` - User currency/economy data
- `welcome_config.json` - Welcome system configuration

## Troubleshooting

### "davey library needed" error
This means FFmpeg or audio libraries are missing. Install them:
```bash
pip install discord.py[voice]
```

### SSL Certificate errors on Windows
This is a known Windows issue. Try:
```bash
pip install certifi
python -m certifi
```

### Bot won't connect to Discord
- Verify your TOKEN in `.env` is correct
- Check that the bot has the necessary intents enabled in Developer Portal
- Ensure the bot has been invited to your server with appropriate permissions

## Permissions

For the bot to work properly, ensure it has these permissions:
- Send Messages
- Manage Messages (for purge)
- Manage Channels (for topic updates)
- Connect to Voice
- Speak in Voice Channels
- Use Application Commands

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source. Feel free to use it as a template for your own Discord bot.

## Support

For issues or questions, please open an issue on GitHub.

---

Made with ❤️ using discord.py

# 🤖 RIVX Telegram News Bot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/status-active-brightgreen.svg)](https://github.com/yourusername/rivx-telegram-bot)

An automated bot that posts Twitter updates and cryptocurrency news to Telegram channels.

![Bot Workflow](https://via.placeholder.com/800x400.png?text=Twitter+%26+RSS+-%3E+Bot+-%3E+Telegram+Posts)

## Features

- **Twitter Integration**
  - Auto-posts new tweets (including media)
  - Excludes reply tweets
  - Handles images/videos/GIFs
  - 60-second polling interval

- **RSS News Aggregation**
  - Supports 13+ major crypto news sources
  - HTML-to-Markdown conversion
  - Image extraction from articles
  - Duplicate prevention

- **Core Features**
  - Async/await architecture
  - BeautifulSoup HTML cleaning
  - Docker support
  - Railway deployment ready

## Installation

### Prerequisites
- Python 3.8+
- Telegram bot token ([@BotFather](https://t.me/botfather))
- Twitter API bearer token
- Railway account (optional)

```bash
# Clone repository
git clone https://github.com/yourusername/rivx-telegram-bot.git
cd rivx-telegram-bot

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Create `.env` file:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_channel_chat_id
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_USERNAME=target_twitter_handle
```

2. (Optional) Modify `RSS_FEEDS` in `main.py`

## Usage

```bash
# Local execution
python main.py

# Using Docker
docker build -t rivx-bot .
docker run -d --env-file .env rivx-bot
```

## Deployment
Deploy on https://Railway.app

1. Add environment variables through Railway dashboard
2. Deploy directly from GitHub repository

## Environment Variables

| Variable               | Description               | Required |
|------------------------|---------------------------|----------|
| TELEGRAM_BOT_TOKEN     | From @BotFather           | Yes      |
| TELEGRAM_CHAT_ID       | Channel/group ID          | Yes      |
| TWITTER_BEARER_TOKEN   | Twitter API v2 token      | Yes      |
| TWITTER_USERNAME       | Target Twitter handle     | Yes      |

## RSS Feeds

Default news sources include:

- CoinDesk
- Cointelegraph
- CoinMarketCap
- Decrypt
- The Block
- Bitcoin Magazine
- CryptoPotato
- NewsBTC
- CryptoSlate
- AMBCrypto

Edit `RSS_FEEDS` in `main.py` to customize sources.

## License
Distributed under the MIT License. See LICENSE for details.

## Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)
- [Feedparser](https://feedparser.readthedocs.io/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)

---

Made with ❤️ by Voxy
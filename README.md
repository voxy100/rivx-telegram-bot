# RIVX Telegram News Bot

This bot auto-posts updates from a specific Twitter account and RSS feeds (CoinDesk & CoinTelegraph) to a Telegram channel.

## Features

- Auto-post latest tweets from `@rivxlabs` including media
- Auto-post news from top crypto sources via RSS (CoinDesk, CoinTelegraph)
- Deployable to Railway or any Python hosting platform

## Environment Variables

Create a `.env` file:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

## Deployment

1. Push to GitHub
2. Deploy to [Railway](https://railway.app)
3. Run the bot!

Made with ❤️ by Voxy

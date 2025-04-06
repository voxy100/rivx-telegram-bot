# -*- coding: utf-8 -*-

# Auto-post tweets and RSS news to Telegram
import os
import requests
import time
import feedparser
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# Check for required environment variables
required_env_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "TWITTER_BEARER_TOKEN"]
missing = [var for var in required_env_vars if not os.getenv(var)]
if missing:
    print(f"Error: Missing environment variables: {', '.join(missing)}")
    exit()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_USERNAME = "rivxlabs"
POLL_INTERVAL = 60  # seconds

bot = Bot(token=TELEGRAM_BOT_TOKEN)
HEADERS = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

# Send startup message with error handling
try:
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Telegram bot is connected!")
except Exception as e:
    print(f"Failed to send startup message: {e}")

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print("Twitter API Error:", res.status_code, res.text)
        return None
    data = res.json().get("data")
    return data["id"] if data else None

user_id = get_user_id(TWITTER_USERNAME)
if not user_id:
    print("Bot stopped: Could not fetch Twitter user ID")
    exit()

last_tweet_id = None
last_rss_guids = set()

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss"
]

while True:
    # ============ Twitter Polling ============
    try:
        twitter_url = (
            f"https://api.twitter.com/2/users/{user_id}/tweets"
            f"?max_results=5&tweet.fields=created_at,attachments,referenced_tweets"
            f"&expansions=attachments.media_keys"
            f"&media.fields=url,preview_image_url,type"
        )
        res = requests.get(twitter_url, headers=HEADERS)
        tweets = res.json().get("data", [])
        media = {m["media_key"]: m for m in res.json().get("includes", {}).get("media", [])}

        if tweets:
            latest = tweets[0]

            if any(ref.get("type") == "replied_to" for ref in latest.get("referenced_tweets", [])):
                print("⏩ Skipped reply")
            else:
                tweet_id = latest["id"]
                tweet_text = latest["text"]
                tweet_url = f"https://x.com/{TWITTER_USERNAME}/status/{tweet_id}"

                if tweet_id != last_tweet_id:
                    message = f"""🔊 New tweet from @{TWITTER_USERNAME}:

{tweet_text}

🔗 {tweet_url}"""

                    media_sent = False

                    if "attachments" in latest and "media_keys" in latest["attachments"]:
                        for key in latest["attachments"]["media_keys"]:
                            media_item = media.get(key)
                            if media_item:
                                if media_item["type"] == "photo":
                                    image_url = media_item.get("url") or media_item.get("preview_image_url")
                                    if image_url:
                                        bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image_url, caption=message)
                                        media_sent = True
                                        break
                                elif media_item["type"] in ["video", "animated_gif"]:
                                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"{message}\n🎥 Video/GIF (see tweet)")
                                    media_sent = True
                                    break

                    if not media_sent:
                        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

                    last_tweet_id = tweet_id
    except Exception as e:
        print("Error polling Twitter:", e)

    # ============ RSS News Polling ============
    try:
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            entries = feed.entries[:3] if hasattr(feed, 'entries') else []
            for entry in entries:
                if entry.id not in last_rss_guids:
                    title = entry.title
                    link = entry.link
                    published = getattr(entry, 'published', 'No date')

                    rss_message = f"""📰 *{title}*
{published}
🔗 {link}"""
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=rss_message, parse_mode="Markdown")
                    last_rss_guids.add(entry.id)
    except Exception as e:
        print("Error polling RSS:", e)

    time.sleep(POLL_INTERVAL)
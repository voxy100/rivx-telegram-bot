# main.py - RIVX Telegram Bot (Twitter + RSS Auto Post)
import os
import time
import requests
import feedparser
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
POLL_INTERVAL = 60  # seconds

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss"
]

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("Twitter API Error:", res.status_code, res.text)
        return None
    data = res.json().get("data")
    return data["id"] if data else None

user_id = get_user_id(TWITTER_USERNAME)
if not user_id:
    print("Bot stopped: Could not fetch user ID")
    exit()

print(f"📡 Monitoring Twitter account: @{TWITTER_USERNAME}")

# Track latest tweets and news
last_tweet_id = None
seen_rss_links = set()

while True:
    # ====== TWITTER ======
    try:
        url = (
            f"https://api.twitter.com/2/users/{user_id}/tweets"
            f"?max_results=5&tweet.fields=created_at,attachments,referenced_tweets"
            f"&expansions=attachments.media_keys"
            f"&media.fields=url,preview_image_url,type"
        )
        headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
        res = requests.get(url, headers=headers)
        tweets = res.json().get("data", [])
        media = {m["media_key"]: m for m in res.json().get("includes", {}).get("media", [])}

        if tweets:
            latest = tweets[0]
            if any(ref.get("type") == "replied_to" for ref in latest.get("referenced_tweets", [])):
                print("⏩ Skipped reply tweet")
            else:
                tweet_id = latest["id"]
                if tweet_id != last_tweet_id:
                    tweet_text = latest["text"]
                    tweet_url = f"https://x.com/{TWITTER_USERNAME}/status/{tweet_id}"
                    message = f"🔊 New tweet from @{TWITTER_USERNAME}:

{tweet_text}

🔗 {tweet_url}"

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
                                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message + "
🎥 Video/GIF (see tweet)")
                                    media_sent = True
                                    break

                    if not media_sent:
                        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                    last_tweet_id = tweet_id
    except Exception as e:
        print(f"❌ Twitter fetch error: {e}")

    # ====== RSS ======
    try:
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if entry.link not in seen_rss_links:
                    seen_rss_links.add(entry.link)
                    news = f"📰 New article:
{entry.title}
🔗 {entry.link}"
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=news)
    except Exception as e:
        print(f"❌ RSS fetch error: {e}")

    time.sleep(POLL_INTERVAL)

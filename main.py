# main.py — Twitter + RSS to Telegram Bot
import os, time, requests, feedparser
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# Telegram config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Twitter config
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_USERNAME = "rivxlabs"
HEADERS = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

# RSS config
RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss"
]

POLL_INTERVAL = 60
bot = Bot(token=TELEGRAM_BOT_TOKEN)
bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Bot is connected!")

# --- Twitter logic ---
def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print("Twitter API Error:", res.status_code, res.text)
        return None
    return res.json()["data"]["id"]

user_id = get_user_id(TWITTER_USERNAME)
last_tweet_id = None
rss_seen_links = set()

while True:
    # --- Check Twitter ---
    try:
        url = (
            f"https://api.twitter.com/2/users/{user_id}/tweets"
            f"?max_results=5&tweet.fields=created_at,attachments,referenced_tweets"
            f"&expansions=attachments.media_keys"
            f"&media.fields=url,preview_image_url,type"
        )
        res = requests.get(url, headers=HEADERS)
        tweets = res.json().get("data", [])
        media = {m["media_key"]: m for m in res.json().get("includes", {}).get("media", [])}

        if tweets:
            latest = tweets[0]
            tweet_id = latest["id"]
            tweet_text = latest["text"]
            tweet_url = f"https://x.com/{TWITTER_USERNAME}/status/{tweet_id}"

            if tweet_id != last_tweet_id and not any(ref.get("type") == "replied_to" for ref in latest.get("referenced_tweets", [])):
                message = (
                f"🔊 New tweet from @{TWITTER_USERNAME}:\n\n"
                f"{tweet_text}\n\n"
                f"🔗 {tweet_url}"
           )

{tweet_text}

🔗 {tweet_url}"
                media_sent = False

                if "attachments" in latest and "media_keys" in latest["attachments"]:
                    for key in latest["attachments"]["media_keys"]:
                        media_item = media.get(key)
                        if media_item:
                            if media_item["type"] == "photo":
                                img_url = media_item.get("url") or media_item.get("preview_image_url")
                                if img_url:
                                    bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=img_url, caption=message)
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
        print("Twitter fetch error:", e)

    # --- Check RSS Feeds ---
    try:
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                link = entry.link
                if link not in rss_seen_links:
                    title = entry.title
                    summary = entry.get("summary", "")
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"📰 *{title}*
{summary}
🔗 {link}", parse_mode="Markdown")
                    rss_seen_links.add(link)
    except Exception as e:
        print("RSS fetch error:", e)

    time.sleep(POLL_INTERVAL)

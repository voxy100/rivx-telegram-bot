# main.py - RIVX Telegram News Bot
import os
import asyncio
import requests
import feedparser
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
POLL_INTERVAL = 60  # seconds

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://www.coinmarketcap.com/headlines/news/feed/",
    "https://decrypt.co/feed",
    "https://www.theblock.co/rss.xml",
    "https://cryptopotato.com/feed/",
    "https://cryptonews.com/news/feed/",
    "https://www.newsbtc.com/feed/",
    "https://bitcoinmagazine.com/.rss/full/",
    "https://ethgasstation.info/blog/feed/",
    "https://u.today/rss",
    "https://cryptoslate.com/feed/",
    "https://ambcrypto.com/feed/"
]

# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)
twitter_headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

async def send_telegram_message(text, photo_url=None):
    try:
        if photo_url:
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo_url,
                caption=text,
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=text,
                parse_mode="Markdown"
            )
    except TelegramError as e:
        print(f"Telegram API Error: {e}")

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    res = requests.get(url, headers=twitter_headers)
    if res.status_code != 200:
        print(f"Twitter API Error {res.status_code}: {res.text}")
        return None
    data = res.json().get("data")
    return data["id"] if data else None

async def monitor_twitter(user_id, last_tweet_id):
    try:
        url = (
            f"https://api.twitter.com/2/users/{user_id}/tweets"
            f"?max_results=5"
            f"&tweet.fields=created_at,attachments,referenced_tweets"
            f"&expansions=attachments.media_keys"
            f"&media.fields=url,preview_image_url,type"
            f"&exclude=replies"
        )
        res = requests.get(url, headers=twitter_headers)
        
        if res.status_code != 200:
            print(f"Twitter API Error {res.status_code}: {res.text}")
            return last_tweet_id

        data = res.json()
        tweets = data.get("data", [])
        media = {m["media_key"]: m for m in data.get("includes", {}).get("media", [])}

        new_last_tweet_id = last_tweet_id

        for tweet in reversed(tweets):
            tweet_id = tweet["id"]
            
            if last_tweet_id and tweet_id <= last_tweet_id:
                continue

            tweet_text = tweet["text"]
            tweet_url = f"https://x.com/{TWITTER_USERNAME}/status/{tweet_id}"
            message = f"""🐦 **New Tweet from @{TWITTER_USERNAME}**

{tweet_text}

[View on X]({tweet_url})"""

            media_sent = False
            if "attachments" in tweet and "media_keys" in tweet["attachments"]:
                for key in tweet["attachments"]["media_keys"]:
                    media_item = media.get(key)
                    if media_item:
                        if media_item["type"] == "photo":
                            image_url = media_item.get("url") or media_item.get("preview_image_url")
                            if image_url:
                                await send_telegram_message(message, image_url)
                                media_sent = True
                                break
                        elif media_item["type"] in ["video", "animated_gif"]:
                            await send_telegram_message(f"{message}\n\n🎥 *Video/GIF attached (view on Twitter)*")
                            media_sent = True
                            break

            if not media_sent:
                await send_telegram_message(message)

            new_last_tweet_id = max(new_last_tweet_id, tweet_id) if new_last_tweet_id else tweet_id

        return new_last_tweet_id

    except Exception as e:
        print(f"❌ Twitter fetch error: {str(e)}")
        return last_tweet_id

async def monitor_rss(seen_links):
    try:
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                if entry.link not in seen_links:
                    seen_links.add(entry.link)
                    
                    soup = BeautifulSoup(entry.description, 'html.parser')
                    [x.decompose() for x in soup.find_all(['img', 'script', 'style'])]
                    clean_text = soup.get_text(separator='\n', strip=True)
                    truncated_text = (clean_text[:250] + '…') if len(clean_text) > 250 else clean_text
                    
                    image_url = None
                    if soup.img and 'src' in soup.img.attrs:
                        image_url = soup.img['src']
                    
                    title = entry.title.replace('...', '…')
                    news = f"""📰 *{title}*

{truncated_text}

[Read Full Article]({entry.link})"""
                    
                    await send_telegram_message(news, image_url)
        return seen_links
    except Exception as e:
        print(f"❌ RSS fetch error: {e}")
        return seen_links

async def main():
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "TWITTER_BEARER_TOKEN", "TWITTER_USERNAME"]
    if any(os.getenv(var) is None for var in required_vars):
        print("Missing required environment variables")
        return

    user_id = get_user_id(TWITTER_USERNAME)
    if not user_id:
        print("Bot stopped: Could not fetch user ID")
        return

    print(f"📡 Monitoring Twitter account: @{TWITTER_USERNAME}")
    await send_telegram_message(f"🤖 **Bot Activated**\nMonitoring: @{TWITTER_USERNAME}")

    last_tweet_id = None
    seen_rss_links = set()

    while True:
        last_tweet_id = await monitor_twitter(user_id, last_tweet_id)
        seen_rss_links = await monitor_rss(seen_rss_links)
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
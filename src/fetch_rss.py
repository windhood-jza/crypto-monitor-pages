"""从 RSS 获取加密货币合规新闻"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import feedparser

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, RSS_FEEDS


def fetch_rss_feed(url: str) -> list:
    """获取单个 RSS 源的新闻"""
    try:
        feed = feedparser.parse(url)
        articles = []
        
        for entry in feed.entries[:10]:  # 每个源取前10条
            article = {
                "title": entry.get("title", ""),
                "summary": entry.get("summary", entry.get("description", ""))[:300],
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": "rss",
                "feed_url": url,
            }
            articles.append(article)
        
        return articles
    except Exception as e:
        print(f"Error fetching RSS {url}: {e}")
        return []


def main():
    """主函数"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    all_articles = []
    for feed_url in RSS_FEEDS:
        print(f"Fetching RSS: {feed_url}")
        articles = fetch_rss_feed(feed_url)
        all_articles.extend(articles)
        print(f"  Got {len(articles)} articles")
    
    # 去重
    seen_links = set()
    unique_articles = []
    for a in all_articles:
        if a["link"] not in seen_links:
            seen_links.add(a["link"])
            unique_articles.append(a)
    
    # 保存
    output_file = os.path.join(DATA_DIR, "rss_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unique_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal unique articles: {len(unique_articles)}")
    print(f"Saved to: {output_file}")
    return unique_articles


if __name__ == "__main__":
    main()

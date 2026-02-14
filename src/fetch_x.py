"""从 X/Twitter 获取加密货币合规相关推文"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, SEARCH_QUERIES, X_API_CONFIG


def fetch_tweets(query: str, max_pages: int = 3) -> list:
    """从 twitterapi.io 获取推文"""
    headers = {"X-API-Key": X_API_CONFIG["api_key"]}
    
    all_tweets = []
    cursor = None
    
    for page in range(max_pages):
        params = {
            "query": query,
            "queryType": X_API_CONFIG["query_type"],
        }
        if cursor:
            params["cursor"] = cursor
        
        try:
            resp = requests.get(
                f"{X_API_CONFIG['api_base']}{X_API_CONFIG['endpoint']}",
                headers=headers,
                params=params,
                timeout=X_API_CONFIG["timeout"]
            )
            resp.raise_for_status()
            data = resp.json()
            
            tweets = data.get("tweets", [])
            for t in tweets:
                all_tweets.append({
                    "id": t.get("id"),
                    "text": t.get("text", ""),
                    "created_at": t.get("createdAt"),
                    "author": t.get("author", {}).get("userName", ""),
                    "url": f"https://x.com/{t.get('author', {}).get('userName', '')}/status/{t.get('id')}",
                    "source": "x",
                    "query": query,
                })
            
            cursor = data.get("next_cursor")
            if not cursor:
                break
                
        except Exception as e:
            print(f"Error fetching tweets for '{query}': {e}")
            break
    
    return all_tweets


def main():
    """主函数"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    all_tweets = []
    for query in SEARCH_QUERIES[:3]:  # 限制查询数量
        print(f"Fetching tweets for: {query}")
        tweets = fetch_tweets(query, max_pages=2)
        all_tweets.extend(tweets)
        print(f"  Got {len(tweets)} tweets")
    
    # 去重
    seen_ids = set()
    unique_tweets = []
    for t in all_tweets:
        if t["id"] not in seen_ids:
            seen_ids.add(t["id"])
            unique_tweets.append(t)
    
    # 保存
    output_file = os.path.join(DATA_DIR, "x_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unique_tweets, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal unique tweets: {len(unique_tweets)}")
    print(f"Saved to: {output_file}")
    return unique_tweets


if __name__ == "__main__":
    main()

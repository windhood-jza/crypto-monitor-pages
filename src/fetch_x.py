"""从 X/Twitter 获取加密货币合规相关推文"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, X_API_CONFIG


def load_accounts():
    """从配置文件加载监控账号"""
    config_file = os.path.join(os.path.dirname(__file__), "..", "config", "accounts.json")
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 只返回启用的账号
            return [a for a in config.get("accounts", []) if a.get("enabled", True)]
    return []


def fetch_tweets_by_account(username: str, max_pages: int = 2) -> list:
    """从 twitterapi.io 获取指定账号的推文"""
    headers = {"X-API-Key": X_API_CONFIG["api_key"]}
    
    all_tweets = []
    cursor = None
    
    # 构建查询：来自特定账号，且包含关键词
    keywords = "(crypto OR regulation OR compliance OR SEC OR stablecoin)"
    query = f"from:{username} {keywords}"
    
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
                    "query": f"from:{username}",
                    "account_category": next((a.get("category", "") for a in load_accounts() if a["username"].lower() == username.lower()), ""),
                })
            
            cursor = data.get("next_cursor")
            if not cursor:
                break
                
        except Exception as e:
            print(f"Error fetching tweets for @{username}: {e}")
            break
    
    return all_tweets


def fetch_tweets_by_keyword(query: str, max_pages: int = 2) -> list:
    """从 twitterapi.io 按关键词搜索推文"""
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
                    "account_category": "",
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
    
    # 1. 从配置的账号获取推文
    accounts = load_accounts()
    print(f"Loaded {len(accounts)} accounts from config")
    
    # 优先获取 high priority 账号
    high_priority = [a for a in accounts if a.get("priority") == "high"][:10]
    medium_priority = [a for a in accounts if a.get("priority") == "medium"][:5]
    
    for account in high_priority + medium_priority:
        username = account["username"]
        print(f"Fetching tweets from @{username} ({account.get('category', '')})")
        tweets = fetch_tweets_by_account(username, max_pages=1)
        all_tweets.extend(tweets)
        print(f"  Got {len(tweets)} tweets")
    
    # 2. 按关键词搜索补充
    keyword_queries = [
        "crypto regulation",
        "SEC enforcement",
        "stablecoin compliance"
    ]
    
    for query in keyword_queries[:2]:
        print(f"Fetching tweets for keyword: {query}")
        tweets = fetch_tweets_by_keyword(query, max_pages=1)
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

"""配置文件"""
import os

# X API 配置 (twitterapi.io)
X_API_CONFIG = {
    "api_key": os.getenv("TWITTER_API_KEY", "new1_b1f149a9162b4357baf1a491885d658b"),
    "api_base": "https://api.twitterapi.io",
    "endpoint": "/twitter/tweet/advanced_search",
    "query_type": "Latest",
    "max_pages": 3,
    "timeout": 30,
    "retry": 1,
}

# 搜索关键词 - 加密货币合规相关
SEARCH_QUERIES = [
    "crypto regulation",
    "cryptocurrency compliance",
    "SEC crypto",
    "crypto AML",
    "stablecoin regulation",
    "DeFi regulation",
    "crypto exchange license",
    "cryptocurrency policy",
    "blockchain regulation",
    "crypto KYC",
]

# RSS 新闻源 - 合规相关
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://coindesk.com/arc/outboundfeeds/rss/",
    "https://decrypt.co/feed",
    "https://theblock.co/rss.xml",
]

# 数据目录
DATA_DIR = "data"
OUTPUT_DIR = "docs"

# 分析配置
PRIORITY_LEVELS = {
    "P1": "紧急 - 监管政策变化、重大执法行动、交易所下架",
    "P2": "重要 - 合规指南更新、行业自律、重要诉讼",
    "P3": "一般 - 行业动态、研究报告、一般新闻",
}

# 保留历史报告数量
MAX_HISTORY = 30

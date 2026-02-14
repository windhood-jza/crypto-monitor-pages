"""使用 K2.5 模型分析并分类情报"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, PRIORITY_LEVELS


def analyze_with_k2(content: str) -> dict:
    """调用 K2.5 模型分析内容 - 使用简单规则分析"""
    content_lower = content.lower()
    
    # P1 关键词
    p1_keywords = [
        "sec charges", "sec lawsuit", "enforcement action", "ban", "prohibition",
        "crackdown", "shutdown", "fine", "penalty", "violation",
        "regulatory action", "cease and desist", "settlement",
        "执法", "禁令", "处罚", "罚款", "关闭", "违规"
    ]
    
    # P2 关键词
    p2_keywords = [
        "guidance", "proposal", "framework", "compliance", "licensing",
        "registration", "disclosure", "transparency", "oversight",
        "指南", "合规", "牌照", "注册", "披露"
    ]
    
    # 判断优先级
    priority = "P3"
    if any(k in content_lower for k in p1_keywords):
        priority = "P1"
    elif any(k in content_lower for k in p2_keywords):
        priority = "P2"
    
    # 生成标题（取前20字）
    title = content[:20] + "..." if len(content) > 20 else content
    
    # 生成摘要（取前50字）
    summary = content[:50] + "..." if len(content) > 50 else content
    
    return {
        "priority": priority,
        "title": title,
        "summary": summary,
        "raw_analysis": f"基于关键词匹配分类为 {priority}",
    }


def extract_recommended_accounts(items: list) -> list:
    """从分析内容中提取推荐添加的账号"""
    import re
    from collections import Counter
    
    # 提取所有 @提及的账号
    mentioned_accounts = []
    for item in items:
        text = item.get("text", "") + " " + item.get("summary", "")
        matches = re.findall(r'@(\w{3,15})', text)
        mentioned_accounts.extend(matches)
    
    # 统计频率
    account_counts = Counter(mentioned_accounts)
    
    # 获取当前监控的账号列表
    current_accounts = set()
    config_file = os.path.join(os.path.dirname(__file__), "..", "config", "accounts.json")
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            current_accounts = {a["username"].lower() for a in config.get("accounts", [])}
    
    # 过滤已监控的账号，返回推荐列表
    recommendations = []
    for username, count in account_counts.most_common(10):
        if username.lower() not in current_accounts and count >= 2:
            # 判断类别
            category = "未知"
            if any(k in username.lower() for k in ["sec", "cftc", "fed", "treasury"]):
                category = "监管"
            elif any(k in username.lower() for k in ["coinbase", "kraken", "binance", "exchange"]):
                category = "交易所"
            elif any(k in username.lower() for k in ["foundation", "labs", "dao"]):
                category = "项目方"
            
            recommendations.append({
                "username": username,
                "category": category,
                "mention_count": count,
                "reason": f"在 {count} 条内容中被提及"
            })
    
    return recommendations[:5]  # 返回前5个


def main():
    """主函数"""
    # 加载数据
    x_data = []
    rss_data = []
    
    x_file = os.path.join(DATA_DIR, "x_data.json")
    rss_file = os.path.join(DATA_DIR, "rss_data.json")
    
    if os.path.exists(x_file):
        with open(x_file, "r", encoding="utf-8") as f:
            x_data = json.load(f)
    
    if os.path.exists(rss_file):
        with open(rss_file, "r", encoding="utf-8") as f:
            rss_data = json.load(f)
    
    print(f"Loaded {len(x_data)} tweets, {len(rss_data)} articles")
    
    # 分析所有内容
    analyzed_items = []
    
    # 分析推文
    for item in x_data[:15]:  # 限制分析数量
        print(f"Analyzing tweet: {item.get('text', '')[:30]}...")
        analysis = analyze_with_k2(item.get("text", ""))
        analyzed_items.append({
            **item,
            **analysis,
            "type": "tweet",
        })
    
    # 分析 RSS 文章
    for item in rss_data[:15]:
        print(f"Analyzing article: {item.get('title', '')[:30]}...")
        content = f"{item.get('title', '')} {item.get('summary', '')}"
        analysis = analyze_with_k2(content)
        analyzed_items.append({
            **item,
            **analysis,
            "type": "article",
        })
    
    # 按优先级排序
    priority_order = {"P1": 0, "P2": 1, "P3": 2}
    analyzed_items.sort(key=lambda x: priority_order.get(x["priority"], 3))
    
    # 提取推荐账号
    recommendations = extract_recommended_accounts(analyzed_items)
    
    # 保存分析结果
    output_file = os.path.join(DATA_DIR, "analyzed_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analyzed_items, f, ensure_ascii=False, indent=2)
    
    # 保存推荐账号
    rec_file = os.path.join(DATA_DIR, "recommendations.json")
    with open(rec_file, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=2)
    
    print(f"\nAnalyzed {len(analyzed_items)} items")
    print(f"P1: {sum(1 for i in analyzed_items if i['priority'] == 'P1')}")
    print(f"P2: {sum(1 for i in analyzed_items if i['priority'] == 'P2')}")
    print(f"P3: {sum(1 for i in analyzed_items if i['priority'] == 'P3')}")
    print(f"Recommendations: {len(recommendations)}")
    print(f"Saved to: {output_file}")
    
    return analyzed_items, recommendations


if __name__ == "__main__":
    main()

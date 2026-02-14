"""使用 K2.5 模型分析并分类情报"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, PRIORITY_LEVELS


def analyze_with_k2(content: str) -> dict:
    """调用 K2.5 模型分析内容"""
    # 构建分析提示
    prompt = f"""分析以下加密货币合规相关内容，判断优先级：

内容：{content[:1000]}

请按以下格式回复：
优先级: P1/P2/P3
标题: 一句话标题（20字以内）
摘要: 50字以内摘要
理由: 为什么这样分类

分类标准：
- P1(紧急): 监管政策变化、重大执法行动、交易所下架、禁令
- P2(重要): 合规指南更新、行业自律、重要诉讼、牌照变动
- P3(一般): 行业动态、研究报告、一般新闻、观点分析
"""
    
    try:
        # 通过 OpenClaw 网关调用 K2.5
        import subprocess
        result = subprocess.run(
            ["openclaw", "ask", "--model", "kimi-coding/k2p5", prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        response = result.stdout.strip()
        
        # 解析响应
        priority = "P3"  # 默认
        title = ""
        summary = ""
        
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("优先级:"):
                p = line.replace("优先级:", "").strip()
                if p in ["P1", "P2", "P3"]:
                    priority = p
            elif line.startswith("标题:"):
                title = line.replace("标题:", "").strip()
            elif line.startswith("摘要:"):
                summary = line.replace("摘要:", "").strip()
        
        # 如果没解析到标题，使用内容前20字
        if not title:
            title = content[:20] + "..." if len(content) > 20 else content
        if not summary:
            summary = content[:50] + "..." if len(content) > 50 else content
        
        return {
            "priority": priority,
            "title": title,
            "summary": summary,
            "raw_analysis": response,
        }
    except Exception as e:
        print(f"Analysis error: {e}")
        # 返回默认分析
        return {
            "priority": "P3",
            "title": content[:20] + "..." if len(content) > 20 else content,
            "summary": content[:50] + "..." if len(content) > 50 else content,
            "raw_analysis": "",
        }


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
    
    # 保存分析结果
    output_file = os.path.join(DATA_DIR, "analyzed_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analyzed_items, f, ensure_ascii=False, indent=2)
    
    print(f"\nAnalyzed {len(analyzed_items)} items")
    print(f"P1: {sum(1 for i in analyzed_items if i['priority'] == 'P1')}")
    print(f"P2: {sum(1 for i in analyzed_items if i['priority'] == 'P2')}")
    print(f"P3: {sum(1 for i in analyzed_items if i['priority'] == 'P3')}")
    print(f"Saved to: {output_file}")
    
    return analyzed_items


if __name__ == "__main__":
    main()

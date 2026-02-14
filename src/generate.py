"""生成 HTML 报告 - 简化可靠版本"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "docs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_simple_report():
    """生成简化报告"""
    
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
    
    # 简单的优先级分类
    p1_items = []
    p2_items = []
    p3_items = []
    
    # 处理推文
    for item in x_data[:20]:
        text = item.get("text", "")
        author = item.get("author", "")
        
        # 简单分类
        text_lower = text.lower()
        if any(k in text_lower for k in ["sec", "enforcement", "charges", "lawsuit", "ban", "crackdown", "执法", "禁令"]):
            priority = "P1"
        elif any(k in text_lower for k in ["regulation", "compliance", "guidance", "framework", "监管", "合规"]):
            priority = "P2"
        else:
            priority = "P3"
        
        entry = {
            "title": text[:60] + "..." if len(text) > 60 else text,
            "summary": text,
            "author": author,
            "url": item.get("url", "#"),
            "time": item.get("created_at", "")[:10] if item.get("created_at") else datetime.now().strftime("%Y-%m-%d"),
            "category": item.get("account_category", "未知"),
        }
        
        if priority == "P1":
            p1_items.append(entry)
        elif priority == "P2":
            p2_items.append(entry)
        else:
            p3_items.append(entry)
    
    # 处理 RSS
    for item in rss_data[:10]:
        title = item.get("title", "")
        summary = item.get("summary", "")
        
        title_lower = title.lower()
        if any(k in title_lower for k in ["sec", "enforcement", "charges", "lawsuit", "ban", "crackdown"]):
            priority = "P1"
        elif any(k in title_lower for k in ["regulation", "compliance", "guidance", "framework"]):
            priority = "P2"
        else:
            priority = "P3"
        
        entry = {
            "title": title[:60] + "..." if len(title) > 60 else title,
            "summary": summary[:200] + "..." if len(summary) > 200 else summary,
            "author": item.get("source", "RSS"),
            "url": item.get("link", "#"),
            "time": item.get("published", "")[:10] if item.get("published") else datetime.now().strftime("%Y-%m-%d"),
            "category": "新闻",
        }
        
        if priority == "P1":
            p1_items.append(entry)
        elif priority == "P2":
            p2_items.append(entry)
        else:
            p3_items.append(entry)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 生成 HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加密货币合规情报 - {today}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }}
        header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        header .meta {{ opacity: 0.9; font-size: 14px; }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-card.p1 {{ border-top: 3px solid #e74c3c; }}
        .stat-card.p2 {{ border-top: 3px solid #f39c12; }}
        .stat-card.p3 {{ border-top: 3px solid #3498db; }}
        .stat-card .count {{ font-size: 28px; font-weight: bold; color: #333; }}
        .stat-card .label {{ font-size: 12px; color: #666; margin-top: 4px; }}
        .section {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .section h2 {{ font-size: 18px; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 2px solid #eee; }}
        .section.p1 h2 {{ color: #e74c3c; border-color: #e74c3c; }}
        .section.p2 h2 {{ color: #f39c12; border-color: #f39c12; }}
        .section.p3 h2 {{ color: #3498db; border-color: #3498db; }}
        .item {{ padding: 14px 0; border-bottom: 1px solid #f0f0f0; }}
        .item:last-child {{ border-bottom: none; }}
        .item-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
        .item-title {{ font-weight: 600; color: #333; font-size: 15px; flex: 1; }}
        .item-category {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #e3f2fd; color: #1565c0; }}
        .item-summary {{ color: #666; font-size: 14px; margin-bottom: 8px; line-height: 1.5; }}
        .item-meta {{ display: flex; gap: 12px; font-size: 12px; color: #999; align-items: center; }}
        .item-meta a {{ color: #667eea; text-decoration: none; }}
        .item-meta a:hover {{ text-decoration: underline; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
        .badge-p1 {{ background: #fee; color: #c33; }}
        .badge-p2 {{ background: #fff3e0; color: #e65100; }}
        .badge-p3 {{ background: #e3f2fd; color: #1565c0; }}
        .empty {{ text-align: center; padding: 40px; color: #999; }}
        footer {{ text-align: center; padding: 30px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ 加密货币合规情报监控</h1>
            <div class="meta">生成时间: {today} | 数据来源: X/Twitter + RSS</div>
        </header>
        
        <div class="stats">
            <div class="stat-card p1">
                <div class="count">{len(p1_items)}</div>
                <div class="label">P1 紧急</div>
            </div>
            <div class="stat-card p2">
                <div class="count">{len(p2_items)}</div>
                <div class="label">P2 重要</div>
            </div>
            <div class="stat-card p3">
                <div class="count">{len(p3_items)}</div>
                <div class="label">P3 一般</div>
            </div>
        </div>
'''
    
    # P1 部分
    if p1_items:
        html += '''
        <div class="section p1">
            <h2>🔴 P1 紧急 - 监管执法/重大政策</h2>
'''
        for item in p1_items[:15]:
            html += f'''
            <div class="item">
                <div class="item-header">
                    <span class="badge badge-p1">P1</span>
                    <span class="item-title">{item["title"]}</span>
                    <span class="item-category">{item["category"]}</span>
                </div>
                <div class="item-summary">{item["summary"]}</div>
                <div class="item-meta">
                    <span>@{item["author"]}</span>
                    <span>{item["time"]}</span>
                    <a href="{item["url"]}" target="_blank">查看原文 →</a>
                </div>
            </div>
'''
        html += '        </div>\n'
    else:
        html += '''
        <div class="section p1">
            <h2>🔴 P1 紧急 - 监管执法/重大政策</h2>
            <div class="empty">今日暂无 P1 级别情报</div>
        </div>
'''
    
    # P2 部分
    if p2_items:
        html += '''
        <div class="section p2">
            <h2>🟡 P2 重要 - 合规指南/行业动态</h2>
'''
        for item in p2_items[:15]:
            html += f'''
            <div class="item">
                <div class="item-header">
                    <span class="badge badge-p2">P2</span>
                    <span class="item-title">{item["title"]}</span>
                    <span class="item-category">{item["category"]}</span>
                </div>
                <div class="item-summary">{item["summary"]}</div>
                <div class="item-meta">
                    <span>@{item["author"]}</span>
                    <span>{item["time"]}</span>
                    <a href="{item["url"]}" target="_blank">查看原文 →</a>
                </div>
            </div>
'''
        html += '        </div>\n'
    else:
        html += '''
        <div class="section p2">
            <h2>🟡 P2 重要 - 合规指南/行业动态</h2>
            <div class="empty">今日暂无 P2 级别情报</div>
        </div>
'''
    
    # P3 部分
    if p3_items:
        html += '''
        <div class="section p3">
            <h2>🔵 P3 一般 - 行业新闻/研究报告</h2>
'''
        for item in p3_items[:10]:
            html += f'''
            <div class="item">
                <div class="item-header">
                    <span class="badge badge-p3">P3</span>
                    <span class="item-title">{item["title"]}</span>
                    <span class="item-category">{item["category"]}</span>
                </div>
                <div class="item-summary">{item["summary"]}</div>
                <div class="item-meta">
                    <span>@{item["author"]}</span>
                    <span>{item["time"]}</span>
                    <a href="{item["url"]}" target="_blank">查看原文 →</a>
                </div>
            </div>
'''
        html += '        </div>\n'
    else:
        html += '''
        <div class="section p3">
            <h2>🔵 P3 一般 - 行业新闻/研究报告</h2>
            <div class="empty">今日暂无 P3 级别情报</div>
        </div>
'''
    
    html += '''
        <footer>
            <p>自动生成的加密货币合规情报监控报告</p>
            <p>数据来源: X/Twitter API + RSS 新闻源</p>
        </footer>
    </div>
</body>
</html>
'''
    
    # 保存报告
    report_file = os.path.join(OUTPUT_DIR, f"report-{today}.html")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    # 更新 index.html
    index_file = os.path.join(OUTPUT_DIR, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Report generated: {report_file}")
    print(f"Total items: P1={len(p1_items)}, P2={len(p2_items)}, P3={len(p3_items)}")


if __name__ == "__main__":
    generate_simple_report()

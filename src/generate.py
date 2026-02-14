"""生成 HTML 报告"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from jinja2 import Template

from config import DATA_DIR, MAX_HISTORY, OUTPUT_DIR, PRIORITY_LEVELS


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加密货币合规情报 - {{ date }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }
        header h1 { font-size: 24px; margin-bottom: 8px; }
        header .meta { opacity: 0.9; font-size: 14px; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 16px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card.p1 { border-top: 3px solid #e74c3c; }
        .stat-card.p2 { border-top: 3px solid #f39c12; }
        .stat-card.p3 { border-top: 3px solid #3498db; }
        .stat-card .count { font-size: 28px; font-weight: bold; color: #333; }
        .stat-card .label { font-size: 12px; color: #666; margin-top: 4px; }
        .section { background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .section h2 { font-size: 18px; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 2px solid #eee; }
        .section.p1 h2 { color: #e74c3c; border-color: #e74c3c; }
        .section.p2 h2 { color: #f39c12; border-color: #f39c12; }
        .section.p3 h2 { color: #3498db; border-color: #3498db; }
        .item { padding: 14px 0; border-bottom: 1px solid #f0f0f0; }
        .item:last-child { border-bottom: none; }
        .item-title { font-weight: 600; color: #333; margin-bottom: 6px; font-size: 15px; }
        .item-summary { color: #666; font-size: 14px; margin-bottom: 8px; }
        .item-meta { display: flex; gap: 12px; font-size: 12px; color: #999; }
        .item-meta a { color: #667eea; text-decoration: none; }
        .item-meta a:hover { text-decoration: underline; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .badge-p1 { background: #fee; color: #c33; }
        .badge-p2 { background: #fff3e0; color: #e65100; }
        .badge-p3 { background: #e3f2fd; color: #1565c0; }
        .history { margin-top: 30px; }
        .history h2 { font-size: 16px; margin-bottom: 12px; color: #666; }
        .history-list { display: flex; flex-wrap: wrap; gap: 8px; }
        .history-item { background: white; padding: 8px 16px; border-radius: 20px; font-size: 13px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .history-item a { color: #667eea; text-decoration: none; }
        .history-item.current { background: #667eea; }
        .history-item.current a { color: white; }
        footer { text-align: center; padding: 30px; color: #999; font-size: 12px; }
        @media (max-width: 600px) {
            .container { padding: 12px; }
            header { padding: 20px; }
            .stats { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ 加密货币合规情报监控</h1>
            <div class="meta">生成时间: {{ date }} | 数据来源: X/Twitter + RSS</div>
        </header>
        
        <div class="stats">
            <div class="stat-card p1">
                <div class="count">{{ counts.P1 }}</div>
                <div class="label">P1 紧急</div>
            </div>
            <div class="stat-card p2">
                <div class="count">{{ counts.P2 }}</div>
                <div class="label">P2 重要</div>
            </div>
            <div class="stat-card p3">
                <div class="count">{{ counts.P3 }}</div>
                <div class="label">P3 一般</div>
            </div>
        </div>
        
        {% if items.P1 %}
        <div class="section p1">
            <h2>🔴 P1 紧急 - 监管政策/执法行动</h2>
            {% for item in items.P1 %}
            <div class="item">
                <div class="item-title">{{ item.title }}</div>
                <div class="item-summary">{{ item.summary }}</div>
                <div class="item-meta">
                    <span class="badge badge-p1">P1</span>
                    <span>{{ item.time }}</span>
                    <a href="{{ item.url }}" target="_blank">查看原文 →</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if items.P2 %}
        <div class="section p2">
            <h2>🟡 P2 重要 - 合规指南/行业自律</h2>
            {% for item in items.P2 %}
            <div class="item">
                <div class="item-title">{{ item.title }}</div>
                <div class="item-summary">{{ item.summary }}</div>
                <div class="item-meta">
                    <span class="badge badge-p2">P2</span>
                    <span>{{ item.time }}</span>
                    <a href="{{ item.url }}" target="_blank">查看原文 →</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if items.P3 %}
        <div class="section p3">
            <h2>🔵 P3 一般 - 行业动态/研究报告</h2>
            {% for item in items.P3 %}
            <div class="item">
                <div class="item-title">{{ item.title }}</div>
                <div class="item-summary">{{ item.summary }}</div>
                <div class="item-meta">
                    <span class="badge badge-p3">P3</span>
                    <span>{{ item.time }}</span>
                    <a href="{{ item.url }}" target="_blank">查看原文 →</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if history %}
        <div class="history">
            <h2>📅 历史报告</h2>
            <div class="history-list">
                {% for h in history %}
                <div class="history-item {% if h.current %}current{% endif %}">
                    <a href="{{ h.url }}">{{ h.date }}</a>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <footer>
            <p>自动生成的加密货币合规情报监控报告</p>
            <p>数据来源: X/Twitter API + RSS 新闻源 | 分析模型: K2.5</p>
        </footer>
    </div>
</body>
</html>
'''


def generate_report():
    """生成报告"""
    # 加载分析数据
    data_file = os.path.join(DATA_DIR, "analyzed_data.json")
    if not os.path.exists(data_file):
        print("No analyzed data found")
        return
    
    with open(data_file, "r", encoding="utf-8") as f:
        items = json.load(f)
    
    # 按优先级分组
    grouped = {"P1": [], "P2": [], "P3": []}
    for item in items:
        p = item.get("priority", "P3")
        if p in grouped:
            grouped[p].append(item)
    
    # 限制每类数量
    for p in grouped:
        grouped[p] = grouped[p][:10]
    
    # 准备模板数据
    today = datetime.now().strftime("%Y-%m-%d")
    
    template_items = {"P1": [], "P2": [], "P3": []}
    for p, item_list in grouped.items():
        for item in item_list:
            template_items[p].append({
                "title": item.get("title", "无标题"),
                "summary": item.get("summary", ""),
                "url": item.get("url", item.get("link", "#")),
                "time": item.get("created_at", item.get("published", ""))[:10] if item.get("created_at") or item.get("published") else today,
            })
    
    # 获取历史报告
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    history = []
    for f in sorted(os.listdir(OUTPUT_DIR), reverse=True):
        if f.startswith("report-") and f.endswith(".html"):
            date_str = f[7:-5]  # report-YYYY-MM-DD.html
            history.append({
                "date": date_str,
                "url": f,
                "current": date_str == today
            })
    
    history = history[:MAX_HISTORY]
    
    # 渲染模板
    template = Template(HTML_TEMPLATE)
    html = template.render(
        date=today,
        items=template_items,
        counts={"P1": len(grouped["P1"]), "P2": len(grouped["P2"]), "P3": len(grouped["P3"])},
        history=history
    )
    
    # 保存报告
    report_file = os.path.join(OUTPUT_DIR, f"report-{today}.html")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    # 更新 index.html
    index_file = os.path.join(OUTPUT_DIR, "index.html")
    shutil.copy(report_file, index_file)
    
    print(f"Report generated: {report_file}")
    print(f"Index updated: {index_file}")
    print(f"Total items: P1={len(grouped['P1'])}, P2={len(grouped['P2'])}, P3={len(grouped['P3'])}")


def main():
    """主函数"""
    generate_report()


if __name__ == "__main__":
    main()

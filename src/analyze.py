"""使用 K2.5 模型分析并分类情报"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, PRIORITY_LEVELS


def analyze_with_k2(content: str, source_type: str = "tweet") -> dict:
    """调用 K2.5 模型分析内容"""
    
    # 构建分析提示
    prompt = f"""你是一位加密货币合规专家。请分析以下内容并输出结构化结果。

原始内容：
{content[:1500]}

请按以下格式输出：

【中文标题】：用一句话概括（20字以内）
【中文摘要】：详细摘要（100字以内，包含关键信息）
【优先级】：P1/P2/P3
【分类】：监管政策/执法行动/机构动态/项目更新/市场影响/其他
【影响评估】：正面/负面/中性
【相关代币/项目】：列出可能影响的代币或项目（如有）
【建议行动】：观察者应该采取什么行动

分类标准：
- P1(紧急): 监管政策变化、重大执法行动、交易所下架、禁令、重大安全事件
- P2(重要): 合规指南更新、行业自律、重要诉讼、牌照变动、机构大额持仓变化
- P3(一般): 行业动态、研究报告、一般新闻、观点分析、技术更新

请确保输出格式严格遵循上述模板。"""

    try:
        # 尝试通过 OpenClaw 调用 K2.5
        import subprocess
        result = subprocess.run(
            ["openclaw", "ask", "--model", "kimi-coding/k2p5", prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0 and result.stdout.strip():
            response = result.stdout.strip()
            return parse_k2_response(response, content)
        else:
            # 如果 OpenClaw 失败，使用备用分析
            print(f"OpenClaw failed, using fallback analysis")
            return fallback_analysis(content)
            
    except Exception as e:
        print(f"Analysis error: {e}")
        return fallback_analysis(content)


def parse_k2_response(response: str, original_content: str) -> dict:
    """解析 K2.5 的响应"""
    result = {
        "priority": "P3",
        "title": "",
        "summary": "",
        "category": "其他",
        "impact": "中性",
        "related_tokens": "",
        "suggested_action": "",
        "raw_analysis": response,
    }
    
    lines = response.split("\n")
    current_field = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 提取各字段
        if "【中文标题】" in line or "标题】" in line:
            result["title"] = line.split("】", 1)[-1].strip().replace("：", "").replace(":", "")
        elif "【中文摘要】" in line or "摘要】" in line:
            result["summary"] = line.split("】", 1)[-1].strip().replace("：", "").replace(":", "")
        elif "【优先级】" in line or "优先级】" in line:
            p = line.split("】", 1)[-1].strip().replace("：", "").replace(":", "")
            if "P1" in p:
                result["priority"] = "P1"
            elif "P2" in p:
                result["priority"] = "P2"
            else:
                result["priority"] = "P3"
        elif "【分类】" in line or "分类】" in line:
            result["category"] = line.split("】", 1)[-1].strip().replace("：", "").replace(":", "")
        elif "【影响评估】" in line or "影响】" in line:
            result["impact"] = line.split("】", 1)[-1].strip().replace("：", "").replace(":", "")
        elif "【相关代币" in line or "代币】" in line:
            result["related_tokens"] = line.split("】", 1)[-1].strip().replace("：", "").replace(":", "")
        elif "【建议行动】" in line or "行动】" in line or "建议】" in line:
            result["suggested_action"] = line.split("】", 1)[-1].strip().replace("：", "").replace(":", "")
    
    # 如果没有解析到标题，使用原文前20字
    if not result["title"]:
        result["title"] = original_content[:20] + "..." if len(original_content) > 20 else original_content
    
    # 如果没有解析到摘要，使用原文前100字
    if not result["summary"]:
        result["summary"] = original_content[:100] + "..." if len(original_content) > 100 else original_content
    
    return result


def fallback_analysis(content: str) -> dict:
    """备用分析（当 K2.5 不可用时）"""
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
    category = "其他"
    
    if any(k in content_lower for k in p1_keywords):
        priority = "P1"
        category = "执法行动"
    elif any(k in content_lower for k in p2_keywords):
        priority = "P2"
        category = "监管政策"
    
    # 生成中文标题和摘要（简单翻译/概括）
    title = content[:20] + "..." if len(content) > 20 else content
    summary = content[:100] + "..." if len(content) > 100 else content
    
    return {
        "priority": priority,
        "title": title,
        "summary": summary,
        "category": category,
        "impact": "中性",
        "related_tokens": "",
        "suggested_action": "持续关注" if priority == "P3" else "立即评估影响",
        "raw_analysis": "基于关键词匹配的备用分析",
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
    
    # 分析推文（限制数量避免超时）
    for i, item in enumerate(x_data[:10]):  # 限制分析数量避免超时
        print(f"[{i+1}/10] Analyzing tweet from @{item.get('author', 'unknown')}...")
        content = item.get("text", "")
        analysis = analyze_with_k2(content, "tweet")
        analyzed_items.append({
            **item,
            **analysis,
            "type": "tweet",
        })
    
    # 分析 RSS 文章
    for i, item in enumerate(rss_data[:5]):
        print(f"[{i+1}/5] Analyzing article: {item.get('title', '')[:30]}...")
        content = f"{item.get('title', '')} {item.get('summary', '')}"
        analysis = analyze_with_k2(content, "article")
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

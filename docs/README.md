# 加密货币合规情报监控系统

## 系统架构

```
数据收集层 → AI分析层 → 报告生成层 → 部署层
```

## 文件结构

```
crypto-compliance/
├── src/
│   ├── config.py          # 配置
│   ├── fetch_x.py         # X/Twitter 数据
│   ├── fetch_rss.py       # RSS 新闻
│   ├── analyze.py         # AI 分析
│   └── generate.py        # 报告生成
├── docs/                  # 输出目录
├── .github/workflows/     # GitHub Actions
└── requirements.txt
```

## 优先级分类

- **P1**: 监管政策、执法行动、交易所下架
- **P2**: 合规指南、行业自律、重要诉讼
- **P3**: 行业动态、研究报告、一般新闻

## 访问地址

https://windhood-jza.github.io/crypto-monitor-pages/

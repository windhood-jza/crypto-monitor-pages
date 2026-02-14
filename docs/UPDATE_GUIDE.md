# 配置更新指引

## 如何添加监控账号

### 方式：直接编辑 GitHub 文件

**步骤 1**：打开配置文件
```
https://github.com/windhood-jza/crypto-monitor-pages/edit/main/config/accounts.json
```

**步骤 2**：在 `accounts` 数组中添加新账号

```json
{
  "username": "新账号名",
  "category": "监管",
  "priority": "high",
  "enabled": true
}
```

**字段说明**：
- `username`: X/Twitter 账号名（不需要 @ 符号）
- `category`: 分类（监管/交易所/项目方/KOL/媒体/人物）
- `priority`: 优先级（high/medium/low）
- `enabled`: 是否启用（true/false）

**步骤 3**：提交更改
- 填写提交信息，例如：`添加 @SECGov 到监控列表`
- 点击 "Commit changes"

**步骤 4**：等待生效
- 下次定时任务自动生效（每天 2 次）
- 或手动触发 GitHub Actions 立即生效

---

## 如何添加关键词

在 `accounts.json` 的 `keywords` 数组中添加：

```json
"keywords": [
  "SEC",
  "regulation",
  "你的新关键词"
]
```

---

## 如何添加 RSS 源

在 `accounts.json` 的 `rss_feeds` 数组中添加：

```json
"rss_feeds": [
  "https://cointelegraph.com/rss",
  "https://你的新rss源.com/feed"
]
```

---

## LLM 辅助更新指令

如果你使用 LLM 辅助更新，可以使用以下指令模板：

```
任务：更新加密货币合规监控配置

当前配置地址：https://github.com/windhood-jza/crypto-monitor-pages/blob/main/config/accounts.json

我的修改要求：
1. 添加账号：@xxx (类别: xxx, 优先级: xxx)
2. 删除账号：@xxx
3. 修改账号 @xxx 的优先级为 high

请读取当前配置，生成更新后的完整 JSON，并告诉我需要修改的具体内容。
```

---

## 身份验证

- 只有 GitHub 用户 `windhood-jza` 的修改会被接受
- 其他用户的修改将被拒绝并记录

---

## 生效时间

| 操作 | 生效时间 |
|------|---------|
| 修改配置 | 下次定时任务（每天 2 次）|
| 手动触发 | 立即生效 |

手动触发方式：
1. 打开 https://github.com/windhood-jza/crypto-monitor-pages/actions
2. 选择 "Daily Update" 工作流
3. 点击 "Run workflow"

# 🧠 悠悠记忆搜索技能

> 语义搜索 + 关键词搜索，让悠悠更好地记住重要的事。

## 配置说明

### 方式 1：使用 SearXNG（已配置，免费）

悠悠已经配置了 SearXNG 本地搜索，可以替代 Brave Search：

```bash
cd /home/admin/.openclaw/workspace/skills/searxng
uv run scripts/searxng.py search "query" --language zh -n 10
```

### 方式 2：配置 Embedding（可选，用于语义搜索）

如果需要更强大的语义搜索，可以配置 Embedding Provider：

**推荐：Voyage AI**（性价比高）
- 免费额度：每月 50 万 tokens
- 配置方式：
  1. 注册：https://voyage.ai/
  2. 获取 API Key
  3. 运行：
  ```bash
  openclaw config set agents.defaults.embedding.provider voyage
  openclaw config set agents.defaults.embedding.apiKey "你的 API Key"
  ```

**备选：OpenAI Embedding**
- 如果你已经有 OpenAI API Key：
  ```bash
  openclaw config set agents.defaults.embedding.provider openai
  openclaw config set agents.defaults.embedding.apiKey "你的 API Key"
  ```

### 方式 3：使用阿里云百炼 Embedding（国内推荐）

阿里云百炼提供免费的 Embedding API：
- 文档：https://help.aliyun.com/zh/dashscope/developer-reference/api-details
- 配置：
  ```bash
  openclaw config set agents.defaults.embedding.provider dashscope
  openclaw config set agents.defaults.embedding.apiKey "你的百炼 API Key"
  ```

---

## 当前状态

| 功能 | 状态 | 说明 |
|------|------|------|
| SearXNG 搜索 | ✅ 已配置 | 免费，本地部署 |
| Jina Reader | ✅ 已配置 | 读取网页内容 |
| Brave Search | ❌ 未配置 | 需要 API Key |
| Embedding 搜索 | ❌ 未配置 | 需要 API Key |

---

## 使用建议

**对于悠悠的当前阶段：**
- ✅ SearXNG 已经足够用于 web 搜索
- ✅ Jina Reader 可以读取 X (Twitter) 等复杂网页
- ⏳ Embedding 搜索可以等以后需要时再配置

**优先事项：**
1. 先用好现有的 SearXNG 和 Jina
2. 如果茶馆的龙虾们有免费 Embedding 方案，再考虑配置
3. 不要为了配置而配置，够用就好

---

## 测试命令

```bash
# 测试 SearXNG 搜索
cd /home/admin/.openclaw/workspace/skills/searxng
uv run scripts/searxng.py search "OpenClaw AI Agent" --language zh -n 5

# 测试 Jina Reader
curl -s "https://r.jina.ai/https://example.com" | head -20
```

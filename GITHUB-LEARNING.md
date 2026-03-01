# 🐙 悠悠的 GitHub 自主学习配置指南

## 🎯 目标

让悠悠能够：
1. 自动搜索 GitHub 上的优质项目
2. 读取 README 学习新技能
3. 提取有价值的内容到记忆系统
4. 定期更新知识库

---

## 🔑 方式 1：GitHub Personal Access Token（推荐）

### 步骤 1：创建 Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写：
   - **Note**: `悠悠自主学习`
   - **Expiration**: `No expiration`
   - **Scopes**: 勾选 `repo` 和 `read:org`

4. 复制生成的 token（格式：`ghp_xxxxxxxxxxxx`）

### 步骤 2：配置环境变量

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# 或者创建 .env 文件
echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxx" >> /home/admin/.openclaw/workspace/.env
```

### 步骤 3：测试 API

```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/search/repositories?q=openclaw+skill&sort=stars
```

---

## 📚 方式 2：无需 Token（有限访问）

不配置 Token 也可以用，但 API 调用限制为 **60 次/小时**。

---

## 🤖 自主学习脚本

### 创建搜索脚本

```bash
#!/bin/bash
# scripts/github-learn.sh
# 用法：./scripts/github-learn.sh "search query"

set -e

QUERY="$1"
TOKEN="${GITHUB_TOKEN:-}"
WORKSPACE="/home/admin/.openclaw/workspace"

echo "🔍 搜索 GitHub: $QUERY"

# 搜索仓库
if [ -n "$TOKEN" ]; then
  RESULT=$(curl -s -H "Authorization: token $TOKEN" \
    "https://api.github.com/search/repositories?q=$QUERY&sort=stars&order=desc&per_page=10")
else
  RESULT=$(curl -s \
    "https://api.github.com/search/repositories?q=$QUERY&sort=stars&order=desc&per_page=10")
fi

# 提取前 3 个仓库
echo "$RESULT" | jq -r '.items[:3] | .[] | "\(.full_name)|\(.stargazers_count)|\(.html_url)"' | \
while IFS='|' read -r repo stars url; do
  echo ""
  echo "📦 学习：$repo ($stars ⭐)"
  
  # 读取 README
  README_URL="https://r.jina.ai/https://raw.githubusercontent.com/$repo/main/README.md"
  CONTENT=$(curl -s "$README_URL" 2>/dev/null || curl -s "https://r.jina.ai/https://raw.githubusercontent.com/$repo/master/README.md")
  
  if [ -n "$CONTENT" ]; then
    # 写入学习记录
    DATE=$(date '+%Y-%m-%d')
    LEARN_FILE="$WORKSPACE/memory/lessons/github-$DATE-$(echo $repo | tr '/' '-').md"
    
    cat > "$LEARN_FILE" << EOF
# 📦 GitHub 学习：$repo

**来源：** $url  
**Stars:** $stars  
**学习日期：** $DATE

## 核心内容

$CONTENT

---

**最后验证：** $DATE
**状态:** ✅ active
**优先级:** 🟡
EOF
    
    echo "✅ 已保存到：$LEARN_FILE"
  else
    echo "⚠️  无法读取 README"
  fi
done

echo ""
echo "✅ GitHub 学习完成！"
```

### 配置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加：每周一凌晨 3 点自动学习
0 3 * * 1 /home/admin/.openclaw/workspace/scripts/github-learn.sh "openclaw skill" >> /home/admin/.openclaw/logs/github-learn.log 2>&1
0 3 * * 1 /home/admin/.openclaw/workspace/scripts/github-learn.sh "AI agent memory" >> /home/admin/.openclaw/logs/github-learn.log 2>&1
```

---

## 🎯 搜索关键词建议

| 类别 | 关键词 |
|------|--------|
| **OpenClaw 技能** | `openclaw skill`, `openclaw plugin`, `moltbot skill` |
| **记忆系统** | `AI agent memory`, `LLM memory`, `vector memory` |
| **Agent 框架** | `AI agent framework`, `autonomous agent`, `multi agent` |
| **工具集成** | `telegram bot ai`, `qq bot framework`, `web automation` |

---

## 📊 学习流程

```
1. 搜索 GitHub (API)
       ↓
2. 按 Star 排序，取前 3 个
       ↓
3. 用 Jina Reader 读取 README
       ↓
4. 提取核心内容
       ↓
5. 写入 memory/lessons/
       ↓
6. Git 提交并推送
       ↓
7. 下次 consolidation 时整合
```

---

## ⚠️ 注意事项

1. **API 限制**
   - 无 Token: 60 次/小时
   - 有 Token: 5,000 次/小时

2. **内容筛选**
   - 优先学习 Star > 100 的项目
   - 优先学习最近 1 年更新的项目
   - 优先学习有完整文档的项目

3. **知识验证**
   - 每周回顾学过的内容
   - 标记过时或错误的信息
   - 合并重复的知识

---

## 🧪 测试

```bash
# 测试搜索
./scripts/github-learn.sh "openclaw skill"

# 查看学习记录
ls -lh memory/lessons/github-*.md

# 查看日志
tail -f /home/admin/.openclaw/logs/github-learn.log
```

---

_创建于 2026-03-01，悠悠的 GitHub 学习计划_

#!/bin/bash
# 🐙 悠悠的 GitHub 学习脚本（简化版）
# 用法：./scripts/github-learn.sh "repo/repo"

set -e

REPO="$1"
WORKSPACE="/home/admin/.openclaw/workspace"
DATE=$(date '+%Y-%m-%d')

if [ -z "$REPO" ]; then
  echo "❌ 用法：$0 \"owner/repo\""
  echo "示例：$0 \"VoltAgent/awesome-openclaw-skills\""
  exit 1
fi

echo "🐙 悠悠 GitHub 学习"
echo "=================="
echo "仓库：$REPO"
echo "日期：$DATE"
echo ""

# 获取仓库信息
echo "📊 获取仓库信息..."
INFO=$(curl -s "https://api.github.com/repos/$REPO")
STARS=$(echo "$INFO" | jq -r '.stargazers_count // 0')
DESC=$(echo "$INFO" | jq -r '.description // "无描述"')
URL=$(echo "$INFO" | jq -r '.html_url // ""')

echo "⭐ Stars: $STARS"
echo "📝 描述：$DESC"
echo ""

# 读取 README
echo "📖 读取 README..."
README_URL="https://r.jina.ai/https://raw.githubusercontent.com/$REPO/main/README.md"
CONTENT=$(curl -s "$README_URL" 2>/dev/null)

if [ -z "$CONTENT" ] || echo "$CONTENT" | grep -q "404: Not Found"; then
  README_URL="https://r.jina.ai/https://raw.githubusercontent.com/$REPO/master/README.md"
  CONTENT=$(curl -s "$README_URL" 2>/dev/null)
fi

if [ -n "$CONTENT" ] && ! echo "$CONTENT" | grep -q "404: Not Found"; then
  # 写入学习记录
  LEARN_FILE="$WORKSPACE/memory/lessons/github-$(echo $REPO | tr '/' '-').md"
  
  cat > "$LEARN_FILE" << EOF
# 📦 GitHub 学习：$REPO

**来源：** $URL  
**Stars:** $STARS  
**学习日期：** $DATE  
**描述:** $DESC

## 核心内容

$CONTENT

---

**最后验证：** $DATE  
**状态:** ✅ active  
**优先级:** 🟡
EOF
  
  echo "✅ 已保存：$LEARN_FILE"
  
  # Git 提交
  cd "$WORKSPACE"
  git add "$LEARN_FILE"
  git commit -m "🐙 GitHub 学习：$REPO"
  git push origin main 2>&1 || echo "⚠️  Git 推送失败"
  
  echo ""
  echo "✅ GitHub 学习完成！"
else
  echo "❌ 无法读取 README"
  exit 1
fi

#!/bin/bash
# 🐙 悠悠的 GitHub 自主学习脚本
# 用法：./scripts/github-learn.sh "search query"

set -e

QUERY="$1"
TOKEN="${GITHUB_TOKEN:-}"
WORKSPACE="/home/admin/.openclaw/workspace"
DATE=$(date '+%Y-%m-%d')

if [ -z "$QUERY" ]; then
  echo "❌ 用法：$0 \"search query\""
  echo "示例：$0 \"openclaw skill\""
  exit 1
fi

echo "🐙 悠悠 GitHub 学习"
echo "=================="
echo "搜索：$QUERY"
echo "日期：$DATE"
echo ""

# 搜索仓库
if [ -n "$TOKEN" ]; then
  RESULT=$(curl -s -H "Authorization: token $TOKEN" \
    "https://api.github.com/search/repositories?q=$QUERY&sort=stars&order=desc&per_page=5")
else
  echo "⚠️  未配置 GITHUB_TOKEN，使用匿名访问（限 60 次/小时）"
  RESULT=$(curl -s \
    "https://api.github.com/search/repositories?q=$QUERY&sort=stars&order=desc&per_page=5")
fi

# 检查是否有结果
ITEM_COUNT=$(echo "$RESULT" | jq -r '.total_count // 0' 2>/dev/null)
if [ "$ITEM_COUNT" = "0" ] || [ -z "$ITEM_COUNT" ] || [ "$ITEM_COUNT" = "null" ]; then
  echo "❌ 未找到相关仓库"
  exit 1
fi

echo "📊 找到 $ITEM_COUNT 个仓库，学习前 3 个..."
echo ""

# 提取前 3 个仓库
echo "$RESULT" | jq -r '.items[:3] | .[] | "\(.full_name)|\(.stargazers_count)|\(.html_url)|\(.description // "无描述")"' | \
while IFS='|' read -r repo stars url desc; do
  echo "📦 学习：$repo"
  echo "   ⭐ $stars  |  $desc"
  
  # 读取 README（尝试 main 和 master 分支）
  README_URL="https://r.jina.ai/https://raw.githubusercontent.com/$repo/main/README.md"
  CONTENT=$(curl -s "$README_URL" 2>/dev/null)
  
  if [ -z "$CONTENT" ] || echo "$CONTENT" | grep -q "404: Not Found"; then
    README_URL="https://r.jina.ai/https://raw.githubusercontent.com/$repo/master/README.md"
    CONTENT=$(curl -s "$README_URL" 2>/dev/null)
  fi
  
  if [ -n "$CONTENT" ] && ! echo "$CONTENT" | grep -q "404: Not Found"; then
    # 写入学习记录
    LEARN_FILE="$WORKSPACE/memory/lessons/github-$(echo $repo | tr '/' '-').md"
    
    cat > "$LEARN_FILE" << EOF
# 📦 GitHub 学习：$repo

**来源：** $url  
**Stars:** $stars  
**学习日期：** $DATE  
**描述:** $desc

## 核心内容

$CONTENT

---

**最后验证：** $DATE  
**状态:** ✅ active  
**优先级:** 🟡
EOF
    
    echo "   ✅ 已保存：$LEARN_FILE"
  else
    echo "   ⚠️  无法读取 README（可能无 README 或私有仓库）"
  fi
  echo ""
done

# Git 提交
cd "$WORKSPACE"
git add memory/lessons/github-*.md 2>/dev/null || true
if ! git diff --cached --quiet; then
  git commit -m "🐙 GitHub 学习：$QUERY" 2>/dev/null || true
  echo "📤 推送到 GitHub..."
  git push origin main 2>&1 || echo "⚠️  Git 推送失败"
else
  echo "⚠️  无新内容，跳过 Git 提交"
fi

echo ""
echo "✅ GitHub 学习完成！"

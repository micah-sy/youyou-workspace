#!/bin/bash
# 悠悠记忆同步脚本 🧠
# 用法：./scripts/sync-memory.sh [commit_message]

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
cd "$WORKSPACE"

# Git 配置（如果未配置）
if ! git config user.name >/dev/null 2>&1; then
    git config user.email "youyou@openclaw.local"
    git config user.name "悠悠 (Yōuyōu)"
fi

# 添加记忆目录
git add memory/

# 检查是否有更改
if ! git diff --cached --quiet; then
    MSG="${1:-🧠 悠悠记忆自动同步 - $(date '+%Y-%m-%d %H:%M')}"
    git commit -m "$MSG"
    
    # 推送到远程（需要认证）
    echo "📤 推送到 GitHub..."
    git push origin main 2>&1 || {
        echo "⚠️  推送失败：需要配置 GitHub 认证"
        echo "💡 解决方法："
        echo "   1. 创建 GitHub Personal Access Token: https://github.com/settings/tokens"
        echo "   2. 运行：git remote set-url origin https://YOUR_TOKEN@github.com/micah-sy/youyou-workspace.git"
        echo "   3. 重新运行此脚本"
        exit 1
    }
    
    echo "✅ 记忆同步完成！"
else
    echo "✨ 记忆无变化，跳过同步"
fi

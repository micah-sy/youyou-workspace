#!/bin/bash
# QQ Bot 记忆同步脚本

WORKSPACE="/home/admin/.openclaw/workspace"
cd "$WORKSPACE"

# Git 配置
if ! git config user.name >/dev/null 2>&1; then
    git config user.email "youyou@openclaw.local"
    git config user.name "悠悠 (Yōuyōu)"
fi

# 添加记忆目录
git add memory/

# 检查是否有更改
if ! git diff --cached --quiet; then
    MSG="🧠 QQ 记忆同步 - $(date '+%Y-%m-%d %H:%M')"
    git commit -m "$MSG"
    
    # 推送
    git push origin main 2>&1 || {
        echo "⚠️  推送失败"
        exit 1
    }
    
    echo "✅ QQ 记忆同步完成！"
else
    echo "✨ 记忆无变化"
fi

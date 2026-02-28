#!/bin/bash
# backup.sh - 悠悠的自动备份脚本
# 用法：./backup.sh [commit_message]

set -euo pipefail

WORKSPACE="/home/admin/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/backup.log"
TIMESTAMP=$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')

cd "$WORKSPACE"

# 检查是否有更改
if git status --porcelain | grep -q .; then
    echo "[$TIMESTAMP] 检测到更改，开始备份..." >> "$LOG_FILE"
    
    # 添加所有更改
    git add -A
    
    # 提交
    MESSAGE="${1:-Auto backup - $TIMESTAMP}"
    git commit -m "$MESSAGE"
    
    echo "[$TIMESTAMP] 备份完成：$MESSAGE" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] 无更改，跳过备份" >> "$LOG_FILE"
fi

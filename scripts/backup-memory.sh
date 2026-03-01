#!/bin/bash
# 🧠 悠悠记忆系统备份脚本
# 用法：./scripts/backup-memory.sh [full|incremental]

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
BACKUP_DIR="/home/admin/.openclaw/backups/memory"
DATE=$(date '+%Y%m%d_%H%M%S')
MODE="${1:-incremental}"

echo "🧠 悠悠记忆系统备份"
echo "===================="
echo "模式：$MODE"
echo "日期：$DATE"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份记忆目录
if [ "$MODE" = "full" ]; then
    echo "📦 全量备份..."
    BACKUP_FILE="$BACKUP_DIR/memory-full-$DATE.tar.gz"
    tar -czf "$BACKUP_FILE" -C "$WORKSPACE" memory/
    echo "✅ 全量备份完成：$BACKUP_FILE"
else
    echo "📦 增量备份..."
    BACKUP_FILE="$BACKUP_DIR/memory-incremental-$DATE.tar.gz"
    # 只备份最近 24 小时修改的文件
    find "$WORKSPACE/memory" -type f -mtime -1 -print0 | \
        tar --null -czf "$BACKUP_FILE" --files-from=- 2>/dev/null || {
        # 如果没有新文件，跳过
        echo "⚠️  无新文件，跳过备份"
        exit 0
    }
    echo "✅ 增量备份完成：$BACKUP_FILE"
fi

# 显示备份大小
BACKUP_SIZE=$(du -h "$BACKUP_FILE" 2>/dev/null | cut -f1)
echo "📊 备份大小：$BACKUP_SIZE"

# 清理旧备份（保留最近 7 天）
echo ""
echo "🗑️  清理 7 天前的备份..."
find "$BACKUP_DIR" -name "memory-*.tar.gz" -mtime +7 -delete
REMAINING=$(ls -1 "$BACKUP_DIR"/memory-*.tar.gz 2>/dev/null | wc -l)
echo "📊 剩余备份数：$REMAINING"

# Git 备份（可选）
if [ -d "$WORKSPACE/.git" ]; then
    echo ""
    echo "📤 Git 备份..."
    cd "$WORKSPACE"
    git add -A
    if ! git diff --cached --quiet; then
        git commit -m "💾 自动备份 - $DATE"
        echo "✅ Git 提交完成"
    else
        echo "⚠️  无更改，跳过 Git 提交"
    fi
fi

echo ""
echo "✅ 备份完成！"
echo "备份位置：$BACKUP_DIR"

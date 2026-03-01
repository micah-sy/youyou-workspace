#!/bin/bash
# ☁️ 悠悠记忆系统云同步脚本
# 用法：./scripts/sync-cloud.sh [aliyun|github|all]

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
DATE=$(date '+%Y%m%d_%H%M%S')
MODE="${1:-all}"

echo "☁️ 悠悠记忆系统云同步"
echo "===================="
echo "模式：$MODE"
echo ""

# 方式 1: GitHub 远程备份（已配置）
if [ "$MODE" = "github" ] || [ "$MODE" = "all" ]; then
    echo "📤 GitHub 同步..."
    cd "$WORKSPACE"
    git pull --rebase 2>/dev/null || true
    git add -A
    if ! git diff --cached --quiet; then
        git commit -m "☁️ 云备份 - $DATE"
        git push origin main 2>&1 || {
            echo "⚠️  GitHub 推送失败（可能是网络问题）"
        }
    else
        echo "⚠️  无更改，跳过 GitHub 同步"
    fi
    echo "✅ GitHub 同步完成"
fi

# 方式 2: 阿里云 OSS 备份（可选）
if [ "$MODE" = "aliyun" ] || [ "$MODE" = "all" ]; then
    if command -v ossutil64 &> /dev/null; then
        echo "📤 阿里云 OSS 同步..."
        ossutil64 cp -r "$WORKSPACE/memory/" "oss://your-bucket/memory-backup/$DATE/" 2>&1 || {
            echo "⚠️  阿里云 OSS 未配置或同步失败"
        }
    else
        echo "⚠️  ossutil64 未安装，跳过阿里云 OSS 备份"
        echo "💡 安装：https://help.aliyun.com/document_detail/50452.html"
    fi
fi

echo ""
echo "✅ 云同步完成！"

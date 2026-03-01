#!/bin/bash
# 🔄 OpenClaw 版本检查脚本
# 用法：./scripts/check-openclaw-update.sh

set -e

DATE=$(date '+%Y-%m-%d %H:%M')
LOG_FILE="/home/admin/.openclaw/logs/update-check.log"

echo "[$DATE] 开始检查 OpenClaw 更新..." >> "$LOG_FILE"

# 获取当前版本
CURRENT_VERSION=$(openclaw --version 2>/dev/null || echo "unknown")
echo "[$DATE] 当前版本：$CURRENT_VERSION" >> "$LOG_FILE"

# 获取最新版本
LATEST_VERSION=$(npm view openclaw version 2>/dev/null || echo "unknown")
echo "[$DATE] 最新版本：$LATEST_VERSION" >> "$LOG_FILE"

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
  echo "[$DATE] ✅ 已是最新版本" >> "$LOG_FILE"
  echo "✅ OpenClaw 已是最新版本 ($CURRENT_VERSION)"
  exit 0
fi

# 有新版本
echo "[$DATE] ⚠️  发现新版本：$LATEST_VERSION" >> "$LOG_FILE"

# 创建更新消息
MESSAGE="🔄 OpenClaw 有新版本可用！

当前版本：$CURRENT_VERSION
最新版本：$LATEST_VERSION

更新命令：
\`\`\`
openclaw update
\`\`\`

更新前建议：
1. 备份配置文件 (~/.openclaw/openclaw.json)
2. 备份技能目录 (~/.openclaw/workspace/)
3. 查看更新日志

需要悠悠帮你更新吗？回复"更新"即可～ 🐣"

# 保存到临时文件（供后续发送）
echo "$MESSAGE" > /tmp/openclaw-update-notice.txt

echo "⚠️  发现新版本：$LATEST_VERSION"
echo "📝 更新通知已保存到 /tmp/openclaw-update-notice.txt"
echo ""
echo "$MESSAGE"

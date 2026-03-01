#!/bin/bash
# 悠悠 QQ Bot 同步配置脚本 🐧
# 用法：./scripts/sync-qq.sh

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
QQBOT_DATA="/home/admin/.openclaw/qqbot/data"

echo "🐧 悠悠 QQ Bot 同步配置"
echo "====================="

# 1. 创建 QQ 聊天 ID 文件
if [ ! -f "$WORKSPACE/.qq-chat-id" ]; then
    echo "📝 创建 QQ 聊天 ID 文件..."
    # 从 known-users.json 读取第一个用户的 openid
    OPENID=$(cat "$QQBOT_DATA/known-users.json" 2>/dev/null | jq -r '.[0].openid' 2>/dev/null || echo "")
    if [ -n "$OPENID" ]; then
        echo "$OPENID" > "$WORKSPACE/.qq-chat-id"
        echo "✅ QQ 聊天 ID 已保存：$OPENID"
    else
        echo "⚠️  未找到 QQ 用户记录，请先和 QQ Bot 互动一次"
        exit 1
    fi
fi

# 2. 同步记忆配置到 QQ Bot 技能目录
echo "📦 同步记忆配置到 QQ Bot..."
mkdir -p "$WORKSPACE/.qqbot-memory"

# 3. 创建 QQ Bot 专用的记忆同步脚本
cat > "$WORKSPACE/scripts/sync-qq-memory.sh" << 'QQEOF'
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
QQEOF

chmod +x "$WORKSPACE/scripts/sync-qq-memory.sh"

echo ""
echo "✅ QQ Bot 同步配置完成！"
echo ""
echo "📱 QQ 聊天 ID: $(cat $WORKSPACE/.qq-chat-id)"
echo "🔄 同步脚本：$WORKSPACE/scripts/sync-qq-memory.sh"
echo ""
echo "💡 使用方法："
echo "   1. QQ 上的对话会自动记录到 memory/YYYY-MM-DD.md"
echo "   2. 每天凌晨 4 点 consolidation 后自动同步到 GitHub"
echo "   3. 手动同步：./scripts/sync-qq-memory.sh"

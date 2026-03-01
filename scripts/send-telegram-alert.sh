#!/bin/bash
# send-telegram-alert.sh - 发送 Telegram 告警
# 用法：./send-telegram-alert.sh "告警内容" [严重级别]
# 严重级别：info(信息) | warning(警告) | critical(严重)

set -euo pipefail

# Telegram 配置
TELEGRAM_BOT_TOKEN="8628526164:AAEdn4P2HBAaDR9sLUZIX1IkW5GuHSgEpC4"
TELEGRAM_CHAT_ID_FILE="/home/admin/.openclaw/workspace/.telegram-chat-id"
ALERT_LOG="/home/admin/.openclaw/workspace/logs/alerts.md"
TIMESTAMP=$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')

# 颜色 emoji
declare -A EMOJIS=(
    ["info"]="ℹ️"
    ["warning"]="⚠️"
    ["critical"]="🔴"
    ["success"]="✅"
    ["error"]="❌"
)

# 读取 Chat ID
get_chat_id() {
    if [[ -f "$TELEGRAM_CHAT_ID_FILE" ]]; then
        cat "$TELEGRAM_CHAT_ID_FILE"
    else
        echo ""
    fi
}

# 保存 Chat ID
save_chat_id() {
    local chat_id="$1"
    echo "$chat_id" > "$TELEGRAM_CHAT_ID_FILE"
    chmod 600 "$TELEGRAM_CHAT_ID_FILE"
}

# 发送消息
send_message() {
    local chat_id="$1"
    local message="$2"
    local parse_mode="Markdown"
    
    local response
    response=$(curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$chat_id" \
        -d "text=$message" \
        -d "parse_mode=$parse_mode" \
        2>/dev/null)
    
    if echo "$response" | grep -q '"ok":true'; then
        return 0
    else
        echo "$response" >&2
        return 1
    fi
}

# 获取 Chat ID（通过发送消息给用户）
get_my_chat_id() {
    echo "🔍 正在获取你的 Chat ID..."
    echo ""
    echo "请在 Telegram 中给我的 Bot 发送任意消息，然后按回车..."
    read -p ""
    
    # 获取最新消息
    local response
    response=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates" 2>/dev/null)
    
    local chat_id
    chat_id=$(echo "$response" | grep -o '"chat":{"id":[0-9-]*' | head -1 | grep -o '[0-9-]*')
    
    if [[ -n "$chat_id" ]]; then
        echo "✅ 获取到 Chat ID: $chat_id"
        save_chat_id "$chat_id"
        echo "✅ Chat ID 已保存到：$TELEGRAM_CHAT_ID_FILE"
        
        # 发送测试消息
        send_test_message "$chat_id"
        return 0
    else
        echo "❌ 未能获取 Chat ID"
        echo "请确保：1) 已启动 Bot 2) 给 Bot 发送了消息"
        return 1
    fi
}

# 发送测试消息
send_test_message() {
    local chat_id="${1:-$(get_chat_id)}"
    
    if [[ -z "$chat_id" ]]; then
        echo "❌ 未配置 Chat ID"
        echo "请先运行：$0 --setup"
        return 1
    fi
    
    local message="🐣 *悠悠的告警系统测试*

✅ 告警通知配置成功！

*时间：* $TIMESTAMP
*级别：* 测试
*说明：* 如果你收到这条消息，说明 Telegram 告警功能已正常工作。

---
_悠悠守护中..._ 🛡️"
    
    if send_message "$chat_id" "$message"; then
        echo "✅ 测试消息已发送"
        return 0
    else
        echo "❌ 发送失败"
        return 1
    fi
}

# 发送告警
send_alert() {
    local alert_text="$1"
    local level="${2:-warning}"
    local emoji="${EMOJIS[$level]:-⚠️}"
    
    local chat_id
    chat_id=$(get_chat_id)
    
    if [[ -z "$chat_id" ]]; then
        echo "❌ 未配置 Chat ID"
        echo "请先运行：$0 --setup"
        return 1
    fi
    
    # 格式化告警消息
    local message="$emoji *网关告警*

*时间：* $TIMESTAMP
*级别：* $level
*内容：*
$alert_text

---
_请检查服务器状态_ 🛡️"
    
    if send_message "$chat_id" "$message"; then
        echo "✅ 告警已发送"
        return 0
    else
        echo "❌ 发送失败"
        return 1
    fi
}

# 显示使用说明
show_help() {
    cat << 'EOF'
Telegram 告警配置工具

用法:
  ./send-telegram-alert.sh --setup     # 配置 Chat ID
  ./send-telegram-alert.sh --test      # 发送测试消息
  ./send-telegram-alert.sh "内容"      # 发送告警
  ./send-telegram-alert.sh --help      # 显示帮助

示例:
  # 首次配置
  ./send-telegram-alert.sh --setup
  
  # 测试
  ./send-telegram-alert.sh --test
  
  # 发送告警
  ./send-telegram-alert.sh "Gateway 进程异常" critical

EOF
}

# 主流程
main() {
    local action="${1:-}"
    
    case "$action" in
        --setup)
            get_my_chat_id
            ;;
        --test)
            send_test_message
            ;;
        --help|-h)
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            send_alert "$action" "${2:-warning}"
            ;;
    esac
}

main "$@"

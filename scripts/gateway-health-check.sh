#!/bin/bash
# gateway-health-check.sh - Gateway 健康检查脚本
# 用法：./gateway-health-check.sh [--send-alert]

set -euo pipefail

LOG_FILE="/home/admin/.openclaw/workspace/logs/health-check.log"
ALERT_LOG="/home/admin/.openclaw/workspace/logs/alerts.md"
TIMESTAMP=$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')
ALERT_THRESHOLD=3  # 连续失败 3 次才告警

# 计数器文件
COUNTER_FILE="/tmp/gateway-health-fail-count"

log() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

send_alert() {
    local message="$1"
    local alert_file="$ALERT_LOG"
    
    # 写入告警文件
    cat >> "$alert_file" << EOF

## 🔴 告警 - $TIMESTAMP

**类型:** $message
**级别:** 严重
**需要立即处理**

EOF
    
    # 发送 Telegram 告警
    local script_dir
    script_dir="$(dirname "$0")"
    if [[ -x "$script_dir/send-telegram-alert.sh" ]]; then
        "$script_dir/send-telegram-alert.sh" "$message" "critical" >> "$LOG_FILE" 2>&1 || true
    fi
    
    log "ALERT: $message (Telegram 告警已发送)"
}

# 检查 1: Gateway 进程
check_gateway_process() {
    log "检查 Gateway 进程..."
    
    if pgrep -f "openclaw gateway" > /dev/null; then
        log "✅ Gateway 进程运行中"
        return 0
    else
        log "❌ Gateway 进程未运行"
        return 1
    fi
}

# 检查 2: Gateway 端口
check_gateway_port() {
    log "检查 Gateway 端口 (10004)..."
    
    if ss -tlnp | grep -q ":10004"; then
        log "✅ Gateway 端口监听中"
        return 0
    else
        log "❌ Gateway 端口未监听"
        return 1
    fi
}

# 检查 3: Gateway API 健康探测
check_gateway_api() {
    log "检查 Gateway API 健康..."
    
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        "http://localhost:10004/health" 2>/dev/null || echo "000")
    
    if [[ "$response" == "200" ]]; then
        log "✅ Gateway API 响应正常 (HTTP $response)"
        return 0
    else
        log "❌ Gateway API 无响应 (HTTP $response)"
        return 1
    fi
}

# 检查 4: Telegram Bot 状态
check_telegram_bot() {
    log "检查 Telegram Bot 状态..."
    
    # 读取配置中的 bot token
    local token
    token=$(grep -o '"botToken"[[:space:]]*:[[:space:]]*"[^"]*"' \
        /home/admin/.openclaw/openclaw.json | cut -d'"' -f4)
    
    if [[ -z "$token" ]]; then
        log "⚠️ 未找到 Telegram Bot Token"
        return 1
    fi
    
    # 调用 Telegram API 检查 bot
    local response
    response=$(curl -s "https://api.telegram.org/bot$token/getMe" 2>/dev/null)
    
    if echo "$response" | grep -q '"ok":true'; then
        log "✅ Telegram Bot 在线"
        return 0
    else
        log "❌ Telegram Bot 离线或 Token 无效"
        return 1
    fi
}

# 检查 5: 阿里云 API 连接
check_aliyun_api() {
    log "检查阿里云 API 连接..."
    
    if aliyun sts get-caller-identity > /dev/null 2>&1; then
        log "✅ 阿里云 API 连接正常"
        return 0
    else
        log "❌ 阿里云 API 连接失败"
        return 1
    fi
}

# 检查 6: 磁盘空间
check_disk_space() {
    log "检查磁盘空间..."
    
    local usage
    usage=$(df /home | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    if [[ "$usage" -lt 80 ]]; then
        log "✅ 磁盘空间正常 (已用 ${usage}%)"
        return 0
    elif [[ "$usage" -lt 90 ]]; then
        log "⚠️ 磁盘空间警告 (已用 ${usage}%)"
        return 0
    else
        log "❌ 磁盘空间不足 (已用 ${usage}%)"
        return 1
    fi
}

# 检查 7: 内存使用
check_memory() {
    log "检查内存使用..."
    
    local usage
    usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    
    if [[ "$usage" -lt 80 ]]; then
        log "✅ 内存使用正常 (${usage}%)"
        return 0
    else
        log "⚠️ 内存使用较高 (${usage}%)"
        return 0
    fi
}

# 主检查流程
main() {
    local send_alert_flag="${1:-}"
    local fail_count=0
    
    log "========== 开始健康检查 =========="
    
    # 执行所有检查
    check_gateway_process || ((fail_count++))
    check_gateway_port || ((fail_count++))
    check_gateway_api || ((fail_count++))
    check_telegram_bot || ((fail_count++))
    check_aliyun_api || ((fail_count++))
    check_disk_space || ((fail_count++))
    check_memory || ((fail_count++))
    
    log "========== 检查完成：失败 $fail_count/7 =========="
    
    # 处理告警逻辑
    if [[ "$fail_count" -gt 0 ]]; then
        # 增加失败计数
        local current_count=0
        [[ -f "$COUNTER_FILE" ]] && current_count=$(cat "$COUNTER_FILE")
        local new_count=$((current_count + 1))
        echo "$new_count" > "$COUNTER_FILE"
        
        log "连续失败次数：$new_count"
        
        # 超过阈值才发送告警
        if [[ "$new_count" -ge "$ALERT_THRESHOLD" ]]; then
            log "达到告警阈值 ($ALERT_THRESHOLD)"
            
            if [[ "$send_alert_flag" == "--send-alert" ]]; then
                send_alert "Gateway 健康检查失败 ($fail_count/7 项)"
            fi
        fi
    else
        # 重置失败计数
        echo "0" > "$COUNTER_FILE"
        log "所有检查通过，重置失败计数"
    fi
    
    # 返回状态码
    [[ "$fail_count" -eq 0 ]] && exit 0 || exit 1
}

# 执行
main "$@"

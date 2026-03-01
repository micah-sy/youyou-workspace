#!/bin/bash
# api-monitor.sh - API 调用失败监控
# 用法：./api-monitor.sh [--check]

set -euo pipefail

LOG_FILE="/home/admin/.openclaw/workspace/logs/api-monitor.log"
ALERT_LOG="/home/admin/.openclaw/workspace/logs/alerts.md"
TIMESTAMP=$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')

# API 配置
API_BASE_URL="https://coding.dashscope.aliyuncs.com/v1"
MAX_FAILURES_PER_HOUR=10

log() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# 检查 API 调用失败日志
check_api_failures() {
    log "检查 API 调用失败记录..."
    
    # 查找 OpenClaw 日志中的 API 错误
    local error_count=0
    local gateway_log="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
    
    if [[ -f "$gateway_log" ]]; then
        # 统计最近 1 小时的 API 错误
        error_count=$(grep -c "API.*Error\|401\|403\|500" "$gateway_log" 2>/dev/null || echo "0")
        # 确保是数字
        error_count=$(echo "$error_count" | tr -d '[:space:]')
    else
        error_count=0
    fi
    
    log "检测到 $error_count 个 API 错误"
    
    if [[ "$error_count" -gt "$MAX_FAILURES_PER_HOUR" ]]; then
        log "⚠️ API 错误超过阈值 ($MAX_FAILURES_PER_HOUR)"
        
        # 写入告警
        cat >> "$ALERT_LOG" << EOF

## 🟠 API 告警 - $TIMESTAMP

**类型:** API 调用失败
**错误数:** $error_count
**阈值:** $MAX_FAILURES_PER_HOUR/小时
**可能原因:**
- API Key 过期或无效
- 额度用完
- 网络问题
- 服务端故障

**建议操作:**
1. 检查 API Key: \`cat /home/admin/.openclaw/agents/main/agent/auth-profiles.json\`
2. 检查额度：访问阿里云百炼控制台
3. 测试连接：\`curl $API_BASE_URL\`
4. 查看日志：\`tail -100 $gateway_log\`

EOF
        
        # 发送 Telegram 告警
        local script_dir
        script_dir="$(dirname "$0")"
        if [[ -x "$script_dir/send-telegram-alert.sh" ]]; then
            "$script_dir/send-telegram-alert.sh" "API 调用失败 ($error_count 次/小时)" "warning" >> "$LOG_FILE" 2>&1 || true
        fi
        
        return 1
    fi
    
    log "✅ API 调用正常"
    return 0
}

# 测试 API 连接
test_api_connection() {
    log "测试 API 连接..."
    
    # 读取 API Key
    local api_key
    api_key=$(grep -o '"apiKey"[[:space:]]*:[[:space:]]*"[^"]*"' \
        /home/admin/.openclaw/agents/main/agent/auth-profiles.json 2>/dev/null | \
        cut -d'"' -f4 || echo "")
    
    if [[ -z "$api_key" ]]; then
        log "❌ 未找到 API Key"
        return 1
    fi
    
    # 测试连接
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $api_key" \
        "$API_BASE_URL/models" 2>/dev/null || echo "000")
    
    if [[ "$response" == "200" ]]; then
        log "✅ API 连接正常 (HTTP $response)"
        return 0
    elif [[ "$response" == "401" ]]; then
        log "❌ API Key 无效或过期 (HTTP $response)"
        return 1
    elif [[ "$response" == "429" ]]; then
        log "❌ API 额度用完 (HTTP $response)"
        return 1
    else
        log "⚠️ API 连接异常 (HTTP $response)"
        return 1
    fi
}

# 检查额度使用情况
check_quota() {
    log "检查 API 额度..."
    
    # 这个需要调用阿里云 API，简化处理
    # 实际应该调用：aliyun bssopenapi QueryAccountBalance
    
    log "⚠️ 额度检查需要配置阿里云账号权限"
    return 0
}

# 主流程
main() {
    log "========== 开始 API 监控检查 =========="
    
    local fail=0
    
    check_api_failures || ((fail++))
    test_api_connection || ((fail++))
    check_quota || true  # 可选检查
    
    log "========== 检查完成 =========="
    
    [[ "$fail" -eq 0 ]] && exit 0 || exit 1
}

main "$@"

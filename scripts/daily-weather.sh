#!/bin/bash
# 🌤️ 悠悠的每日天气推送脚本
# 用法：./scripts/daily-weather.sh

set -e

# 获取用户 Telegram Chat ID
TELEGRAM_CHAT_ID="5452444464"
DATE=$(date '+%Y-%m-%d %H:%M')

echo "[$DATE] 开始发送天气推送..." >> /home/admin/.openclaw/logs/weather.log

# 获取天气信息
WEATHER=$(curl -s "wttr.in/?format=%l:+%c+%t+%h+%w" 2>/dev/null || echo "天气数据获取失败")

echo "[$DATE] 天气数据：$WEATHER" >> /home/admin/.openclaw/logs/weather.log

# 生成天气消息
MESSAGE="🌤️ 悠悠的每日天气推送

$WEATHER

穿衣建议：根据天气情况调整着装哦～ 🐣"

# 使用 OpenClaw message 工具发送 Telegram 消息
# 实际发送由 OpenClaw 的 cron 系统处理
echo "$MESSAGE" > /tmp/weather-message.txt

echo "[$DATE] 天气推送完成" >> /home/admin/.openclaw/logs/weather.log

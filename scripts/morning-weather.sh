#!/bin/bash
# morning-weather.sh - 早晨天气推送脚本
# 用法：./morning-weather.sh

set -euo pipefail

SCRIPT_DIR="$(dirname "$0")"
TOKEN_FILE="$SCRIPT_DIR/../.telegram-chat-id"
WEATHER_SCRIPT="$SCRIPT_DIR/weather-3day-simple.sh"

# 读取 Chat ID
if [[ -f "$TOKEN_FILE" ]]; then
    CHAT_ID=$(cat "$TOKEN_FILE")
else
    echo "❌ 未找到 Telegram Chat ID"
    exit 1
fi

# 读取 Bot Token
BOT_TOKEN="8628526164:AAEdn4P2HBAaDR9sLUZIX1IkW5GuHSgEpC4"

# 获取天气数据
CITY="睢宁"
LOCATION="117.9469,33.9019"
CAIYUN_TOKEN=$(cat "$SCRIPT_DIR/../.caiyun-token" 2>/dev/null)

if [[ -z "$CAIYUN_TOKEN" ]]; then
    echo "❌ 未找到彩云天气 API Token"
    exit 1
fi

# 调用 API 获取数据
API_URL="https://api.caiyunapp.com/v2.6/$CAIYUN_TOKEN/$LOCATION/weather?dailysteps=3"
response=$(curl -s --max-time 10 "$API_URL" 2>/dev/null)

# 使用 Python 生成美观的天气消息
weather_message=$(python3 << EOF
import json
from datetime import datetime

data = json.loads('$response')
if data.get('status') != 'ok':
    print("API 调用失败")
    exit(1)

daily = data['result']['daily']
realtime = data['result']['realtime']

# 当前天气
temp = realtime['temperature']
skycon = realtime['skycon']
humidity = int(realtime['humidity'] * 100)
wind = realtime['wind']['speed']
aqi = realtime['air_quality']['aqi']['chn']

weather_icons = {
    'LIGHT_RAIN': '🌦️',
    'MODERATE_RAIN': '🌧️',
    'HEAVY_RAIN': '⛈️',
    'CLOUDY': '☁️',
    'PARTLY_CLOUDY': '⛅',
    'CLEAR': '☀️',
    'FOG': '🌫️'
}
icon = weather_icons.get(skycon, '🌤️')

# 生成消息
today = datetime.now().strftime('%Y-%m-%d')
weekday = datetime.now().strftime('%A')
weekday_map = {'Monday':'一', 'Tuesday':'二', 'Wednesday':'三', 'Thursday':'四', 'Friday':'五', 'Saturday':'六', 'Sunday':'日'}
weekday_cn = weekday_map.get(weekday, '')

print(f"""🌤️ *睢宁天气预报*
📅 {today}（周{weekday_cn}）

*当前天气：*
{icon} 温度：{temp:.1f}°C
💨 风力：{wind:.1f} km/h
💧 湿度：{humidity}%
😷 AQI: {aqi}

*未来 3 天：*
""")

for i in range(3):
    day = ['今天', '明天', '后天'][i]
    date = daily['astro'][i]['date'].split('T')[0]
    temp_max = daily['temperature'][i]['max']
    temp_min = daily['temperature'][i]['min']
    sky = daily['skycon'][i]['value']
    ico = weather_icons.get(sky, '🌤️')
    prob = int(daily['precipitation'][i]['probability'])
    
    print(f"{day}：{ico} {temp_min:.0f}~{temp_max:.0f}°C 降水{prob}%")

print(f"""
💡 *温馨提示：*
- 早起记得添衣保暖
- {"☔ 带伞，今天有雨" if daily['precipitation'][0]['probability'] > 0.5 else "🌞 天气不错"}
- 数据来自彩云天气

_祝你有美好的一天！_ ✨""")
EOF
)

# 发送 Telegram 消息
send_telegram_message() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$message" \
        -d "parse_mode=Markdown" \
        > /dev/null
}

# 发送消息
if [[ -n "$weather_message" ]]; then
    send_telegram_message "$weather_message"
    echo "✅ 天气推送成功 - $(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')"
else
    echo "❌ 天气数据获取失败"
    exit 1
fi

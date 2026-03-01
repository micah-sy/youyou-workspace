#!/bin/bash
# weather-3day-simple.sh - 3 天天气预报（简洁可视化版）
# 用法：./weather-3day-simple.sh [城市名]

TOKEN=$(cat /home/admin/.openclaw/workspace/.caiyun-token 2>/dev/null)

if [[ -z "$TOKEN" ]]; then
    echo "❌ 未找到 API Token"
    exit 1
fi

CITY="${1:-徐州}"
LOCATION="117.2848,34.2056"  # 徐州坐标

# 获取天气数据
response=$(curl -s --max-time 10 "https://api.caiyunapp.com/v2.6/$TOKEN/$LOCATION/weather?dailysteps=3" 2>/dev/null)

# 使用 python 解析 JSON（更可靠）
python3 << EOF
import json
import sys
from datetime import datetime

data = json.loads('$response')
if data.get('status') != 'ok':
    print("❌ API 调用失败")
    sys.exit(1)

daily = data['result']['daily']
weekdays = ['今天', '明天', '后天']
weather_icons = {
    'LIGHT_RAIN': '🌦️',
    'MODERATE_RAIN': '🌧️',
    'HEAVY_RAIN': '⛈️',
    'CLOUDY': '☁️',
    'PARTLY_CLOUDY': '⛅',
    'CLEAR': '☀️',
    'FOG': '🌫️',
    'SNOW': '❄️'
}

print("")
print("╔════════════════════════════════════════════════════════╗")
print(f"║           🌤️  $CITY 未来 3 天天气预报                  ║")
print("╚════════════════════════════════════════════════════════╝")
print("")

for i in range(3):
    day = weekdays[i]
    date = daily['astro'][i]['date'].split('T')[0]
    temp_max = daily['temperature'][i]['max']
    temp_min = daily['temperature'][i]['min']
    skycon = daily['skycon'][i]['value']
    icon = weather_icons.get(skycon, '🌤️')
    precip_prob = daily['precipitation'][i]['probability']
    wind_max = daily['wind'][i]['max']['speed']
    sunrise = daily['astro'][i]['sunrise']['time']
    sunset = daily['astro'][i]['sunset']['time']
    
    print("┌────────────────────────────────────────────────────────┐")
    print(f"│  {day} ({date})                                │")
    print("├────────────────────────────────────────────────────────┤")
    print(f"│  🌡️  气温：{temp_min:4.1f}°C ~ {temp_max:4.1f}°C                       │")
    print(f"│  🌤️  天气：{icon} {skycon.replace('_', ' ')}                       │")
    print(f"│  ☔  降水：{precip_prob:.0f}%                              │")
    print(f"│  💨  风力：{wind_max:.1f} km/h                            │")
    print(f"│  🌅  日出：{sunrise} · 日落：{sunset}                  │")
    print("└────────────────────────────────────────────────────────┘")
    print("")

print("╭────────────────────────────────────────────────────────────╮")
print(f"│  💡 数据来自彩云天气 · 更新于 {datetime.now().strftime('%Y-%m-%d %H:%M')}              │")
print("╰────────────────────────────────────────────────────────────╯")
print("")
EOF

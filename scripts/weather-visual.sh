#!/bin/bash
# weather-visual.sh - 可视化天气预报（3 天简洁版）
# 用法：./weather-visual.sh [城市名]

set -euo pipefail

# 读取 Token
TOKEN_FILE="/home/admin/.openclaw/workspace/.caiyun-token"
TOKEN=$(cat "$TOKEN_FILE" 2>/dev/null || echo "")

if [[ -z "$TOKEN" ]]; then
    echo "❌ 未找到彩云天气 API Token"
    exit 1
fi

# 城市坐标映射
declare -A CITIES=(
    ["北京"]="116.4075,39.9040"
    ["上海"]="121.4737,31.2304"
    ["广州"]="113.2644,23.1291"
    ["深圳"]="114.0579,22.5431"
    ["杭州"]="120.1551,30.2741"
    ["南京"]="118.7969,32.0603"
    ["武汉"]="114.3054,30.5931"
    ["成都"]="104.0665,30.5723"
    ["西安"]="108.9398,34.3416"
    ["徐州"]="117.2848,34.2056"
    ["睢宁"]="117.9469,33.9019"
)

CITY="${1:-徐州}"
LOCATION="${CITIES[$CITY]:-117.2848,34.2056}"

# 获取天气数据
API_URL="https://api.caiyunapp.com/v2.6/$TOKEN/$LOCATION/weather?dailysteps=3"
response=$(curl -s --max-time 10 "$API_URL" 2>/dev/null)

# 检查状态
status=$(echo "$response" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
if [[ "$status" != "ok" ]]; then
    echo "❌ API 调用失败"
    exit 1
fi

# 天气图标映射
get_weather_icon() {
    case "$1" in
        *"LIGHT_RAIN"*) echo "🌦️" ;;
        *"MODERATE_RAIN"*) echo "🌧️" ;;
        *"HEAVY_RAIN"*) echo "⛈️" ;;
        *"CLOUDY"*) echo "☁️" ;;
        *"PARTLY_CLOUDY"*) echo "⛅" ;;
        *"CLEAR"*) echo "☀️" ;;
        *"FOG"*) echo "🌫️" ;;
        *"SNOW"*) echo "❄️" ;;
        *) echo "🌤️" ;;
    esac
}

# 输出可视化天气预报
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║           🌤️  $CITY 未来 3 天天气预报                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 解析并输出每天的天气
for i in 0 1 2; do
    # 提取日期
    date=$(echo "$response" | grep -o '"date":"[^"]*"' | sed -n "$((i+1))p" | cut -d'"' -f4)
    date_only=$(echo "$date" | cut -d'T' -f1)
    
    # 提取温度
    temp_max=$(echo "$response" | grep -A2 '"temperature"' | grep -o '"max":[0-9.]*' | sed -n "$((i+1))p" | cut -d':' -f2)
    temp_min=$(echo "$response" | grep -A2 '"temperature"' | grep -o '"min":[0-9.]*' | sed -n "$((i+1))p" | cut -d':' -f2)
    
    # 提取天气
    skycon=$(echo "$response" | grep -A2 '"skycon"' | grep -o '"value":"[^"]*"' | sed -n "$((i+1))p" | cut -d'"' -f4)
    weather_icon=$(get_weather_icon "$skycon")
    
    # 提取降水概率
    precip=$(echo "$response" | grep -A3 '"precipitation"' | grep -o '"probability":[0-9]*' | sed -n "$((i+1))p" | cut -d':' -f2)
    
    # 提取风力
    wind_max=$(echo "$response" | grep -A2 '"wind"' | grep -o '"max":{"speed":[0-9.]*' | sed -n "$((i+1))p" | grep -o '[0-9.]*')
    
    # 计算星期
    day_names=("今天" "明天" "后天")
    day_name="${day_names[$i]}"
    
    # 输出
    echo "┌────────────────────────────────────────────────────────┐"
    echo "│  $day_name ($date_only)                                │"
    echo "├────────────────────────────────────────────────────────┤"
    printf "│  %-10s %-10s %-20s           │\n" "天气:" "$weather_icon" "$(echo $skycon | sed 's/_/ /g' | sed 's/.*/\L&/' | sed 's/\b\(.\)/\u\1/g')"
    printf "│  %-10s %-15s %-15s          │\n" "气温:" "${temp_min}°C" "~ ${temp_max}°C"
    printf "│  %-10s %-15s %-15s          │\n" "降水:" "$precip%" "${precip:-0}mm"
    printf "│  %-10s %-15s %-15s          │\n" "风力:" "${wind_max}km/h" ""
    echo "└────────────────────────────────────────────────────────┘"
    echo ""
done

echo "╭────────────────────────────────────────────────────────────╮"
echo "│  💡 提示：数据来自彩云天气 · 更新于 $(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M')  │"
echo "╰────────────────────────────────────────────────────────────╯"
echo ""

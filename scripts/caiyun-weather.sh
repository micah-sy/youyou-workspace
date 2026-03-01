#!/bin/bash
# caiyun-weather.sh - 彩云天气 API 查询脚本
# 用法：./caiyun-weather.sh [城市名] [预报天数]

set -euo pipefail

# 读取 Token
TOKEN_FILE="/home/admin/.openclaw/workspace/.caiyun-token"
if [[ -f "$TOKEN_FILE" ]]; then
    TOKEN=$(cat "$TOKEN_FILE")
else
    echo "❌ 未找到彩云天气 API Token"
    echo "请先配置：echo '你的 Token' > $TOKEN_FILE"
    exit 1
fi

# 城市坐标映射（可以扩展）
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

CITY="${1:-北京}"
DAYS="${2:-3}"

# 获取城市坐标
if [[ -v CITIES["$CITY"] ]]; then
    LOCATION="${CITIES[$CITY]}"
else
    echo "⚠️  未找到城市 '$CITY' 的坐标，使用北京坐标"
    LOCATION="${CITIES[北京]}"
fi

echo "🌤️  $CITY 天气预报"
echo "━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 查询天气 API
API_URL="https://api.caiyunapp.com/v2.6/$TOKEN/$LOCATION/weather?dailysteps=$DAYS"

response=$(curl -s --max-time 10 "$API_URL" 2>/dev/null)

# 解析返回数据
status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [[ "$status" != "ok" ]]; then
    echo "❌ API 调用失败"
    echo "响应：$response"
    exit 1
fi

# 提取实时天气
temp=$(echo "$response" | grep -o '"temperature":[0-9.-]*' | head -1 | cut -d':' -f2)
weather_status=$(echo "$response" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
humidity=$(echo "$response" | grep -o '"humidity":[0-9]*' | head -1 | cut -d':' -f2)
wind_speed=$(echo "$response" | grep -o '"speed":[0-9.]*' | head -1 | cut -d':' -f2)
wind_direction=$(echo "$response" | grep -o '"direction":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "**当前天气：**"
echo "🌡️  温度：${temp}°C"
echo "🌤️  天气：$weather_status"
echo "💧 湿度：${humidity}%"
echo "💨 风速：${wind_speed}m/s $wind_direction"
echo ""

# 提取天气预报
echo "**未来${DAYS}天预报：**"
echo ""

# 简单解析（实际应该用 jq）
echo "$response" | grep -o '"date":"[^"]*"' | head -$DAYS | while read -r date_line; do
    date=$(echo "$date_line" | cut -d'"' -f4)
    echo "📅 $date"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━"
echo "数据来源：彩云天气 · 更新于 $(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')"

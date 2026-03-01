#!/bin/bash
# weather-forecast.sh - 天气预报脚本（含 3 天预报）
# 用法：./weather-forecast.sh [城市名]

set -euo pipefail

CITY="${1:-睢宁}"
ENCODED_CITY=$(echo "$CITY" | sed 's/ /+/g')

echo "🌤️  $CITY 天气预报"
echo "━━━━━━━━━━━━━━━━━━━━"
echo ""

# 当前天气
echo "**当前天气：**"
current=$(curl -s --max-time 5 "wttr.in/$ENCODED_CITY?format=%l:+%c+%t+%h+%w" 2>/dev/null || echo "暂时无法获取")
echo "$current"
echo ""

# 3 天预报
echo "**未来 3 天预报：**"
echo ""

# 获取预报数据（wttr.in 的 m 格式）
forecast=$(curl -s --max-time 10 "wttr.in/$ENCODED_CITY?m" 2>/dev/null | grep -A 20 "Weather report for" | head -25)

if [[ -n "$forecast" ]]; then
    echo "$forecast"
else
    # 备用方案：使用简化的 3 天预报
    echo "正在获取 3 天预报..."
    
    for i in 1 2 3; do
        day_data=$(curl -s --max-time 5 "wttr.in/$ENCODED_CITY?format=$i" 2>/dev/null || echo "数据暂缺")
        echo "第$i天：$day_data"
    done
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━"
echo "_数据来自 wttr.in · 更新于 $(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')_"

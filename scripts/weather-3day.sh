#!/bin/bash
# weather-3day.sh - 3 天天气预报（简洁版）
# 用法：./weather-3day.sh [城市名]

CITY="${1:-睢宁}"

echo "🌤️  $CITY 天气预报"
echo "━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 尝试获取天气数据
weather_data=$(curl -s --max-time 5 "wttr.in/$CITY" 2>/dev/null)

if [[ -n "$weather_data" ]]; then
    # 从完整预报中提取当前 +3 天
    echo "$weather_data" | head -40
else
    # 服务不可用时的备选方案
    echo "⚠️  暂时无法获取天气数据"
    echo ""
    echo "可能的原因："
    echo "  • wttr.in 服务暂时不可用"
    echo "  • 网络连接超时"
    echo "  • 请求频率限制"
    echo ""
    echo "建议："
    echo "  • 稍后再试"
    echo "  • 访问 https://wttr.in/$CITY"
    echo "  • 使用手机天气 App"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━"
echo "更新时间：$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')"

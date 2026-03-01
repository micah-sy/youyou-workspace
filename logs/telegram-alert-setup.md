# 📱 Telegram 告警配置指南

**版本：** v1.0  
**更新时间：** 2026-03-01

---

## 🎯 配置步骤

### 第 1 步：配置 Chat ID

**在配置之前，你需要：**

1. 打开 Telegram
2. 找到我的 Bot（就是你平时聊天的那个）
3. 发送任意消息给 Bot（比如"测试"）

**然后运行配置命令：**

```bash
cd /home/admin/.openclaw/workspace
./scripts/send-telegram-alert.sh --setup
```

**按提示操作：**
```
🔍 正在获取你的 Chat ID...

请在 Telegram 中给我的 Bot 发送任意消息，然后按回车...
[按回车]

✅ 获取到 Chat ID: 123456789
✅ Chat ID 已保存到：/home/admin/.openclaw/workspace/.telegram-chat-id
✅ 测试消息已发送
```

---

### 第 2 步：测试告警

```bash
./scripts/send-telegram-alert.sh --test
```

**你会在 Telegram 收到：**
```
🐣 悠悠的告警系统测试

✅ 告警通知配置成功！

时间：2026-03-01 08:30:00
级别：测试
说明：如果你收到这条消息，说明 Telegram 告警功能已正常工作。

---
悠悠守护中... 🛡️
```

---

### 第 3 步：验证自动告警

手动触发一次健康检查，看看是否正常工作：

```bash
./scripts/gateway-health-check.sh
```

如果没有告警（一切正常），可以模拟一个告警测试：

```bash
# 发送测试告警
./scripts/send-telegram-alert.sh "这是测试告警" warning
```

---

## 📊 告警类型

| 告警类型 | 触发条件 | 级别 |
|---------|---------|------|
| Gateway 进程异常 | Gateway 停止运行 | 🔴 Critical |
| Gateway 端口异常 | 10004 端口未监听 | 🔴 Critical |
| Gateway API 异常 | 健康探测失败 | 🔴 Critical |
| Telegram Bot 离线 | Bot API 无响应 | 🔴 Critical |
| 阿里云 API 异常 | API 连接失败 | 🔴 Critical |
| 磁盘空间不足 | 使用率 >90% | 🔴 Critical |
| API 调用失败 | 错误 >10 次/小时 | ⚠️ Warning |
| API Key 无效 | 认证失败 (401) | 🔴 Critical |
| API 额度用完 | 额度耗尽 (429) | 🔴 Critical |

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `scripts/send-telegram-alert.sh` | Telegram 告警发送脚本 |
| `.telegram-chat-id` | 存储你的 Chat ID（权限 600） |
| `logs/alerts.md` | 告警记录（Markdown 格式） |
| `logs/health-check.log` | 健康检查日志 |
| `logs/api-monitor.log` | API 监控日志 |

---

## 🔧 高级配置

### 修改告警阈值

编辑脚本即可：

```bash
# 编辑健康检查脚本
nano scripts/gateway-health-check.sh

# 修改阈值
ALERT_THRESHOLD=3  # 连续失败 3 次才告警

# 编辑 API 监控脚本
nano scripts/api-monitor.sh

# 修改阈值
MAX_FAILURES_PER_HOUR=10  # 每小时 10 次错误
```

### 自定义告警消息格式

编辑 `send-telegram-alert.sh` 中的 `send_alert()` 函数：

```bash
# 修改消息模板
local message="$emoji *网关告警*

*时间：* $TIMESTAMP
*级别：* $level
*内容：*
$alert_text

---
_请检查服务器状态_ 🛡️"
```

### 添加其他通知方式

在 `send_alert()` 函数中添加：

```bash
# 钉钉机器人
curl 'https://oapi.dingtalk.com/robot/send?access_token=TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"msgtype":"text","text":{"content":"告警：'"$alert_text"'"}}'

# 邮件
echo "$alert_text" | mail -s "网关告警" your@email.com
```

---

## 🛠️ 故障排查

### 问题 1: 收不到告警消息

**检查 Chat ID 是否配置：**
```bash
cat /home/admin/.openclaw/workspace/.telegram-chat-id
```

如果为空或不存在：
```bash
./scripts/send-telegram-alert.sh --setup
```

**检查 Bot 是否在线：**
```bash
curl "https://api.telegram.org/bot8628526164:AAEdn4P2HBAaDR9sLUZIX1IkW5GuHSgEpC4/getMe"
```

应该返回：
```json
{"ok":true,"result":{"id":8628526164,"is_bot":true,"first_name":"...","username":"..."}}
```

### 问题 2: 告警太频繁

**增加阈值：**
```bash
# 编辑脚本
nano scripts/gateway-health-check.sh

# 修改
ALERT_THRESHOLD=5  # 从 3 次改为 5 次
```

**或者禁用某些检查：**
```bash
# 注释掉不需要的检查
# check_disk_space || ((fail_count++))
```

### 问题 3: 想更换告警 Bot

**修改 Token：**
```bash
# 编辑脚本
nano scripts/send-telegram-alert.sh

# 修改
TELEGRAM_BOT_TOKEN="新的 Bot Token"
```

**同时更新 openclaw.json（如果是同一个 Bot）：**
```bash
nano /home/admin/.openclaw/openclaw.json
```

---

## 📝 使用示例

### 发送不同级别的告警

```bash
# 信息（蓝色）
./scripts/send-telegram-alert.sh "系统正常维护中" info

# 警告（黄色）
./scripts/send-telegram-alert.sh "CPU 使用率较高" warning

# 严重（红色）
./scripts/send-telegram-alert.sh "Gateway 进程崩溃" critical
```

### 在脚本中集成告警

```bash
#!/bin/bash
# 你的脚本

if [[ 某个条件 ]]; then
    # 发送告警
    /home/admin/.openclaw/workspace/scripts/send-telegram-alert.sh \
        "你的告警内容" "warning"
fi
```

### 查看告警历史

```bash
# 查看所有告警记录
cat /home/admin/.openclaw/workspace/logs/alerts.md

# 查看今天的告警
grep "$(date +%Y-%m-%d)" /home/admin/.openclaw/workspace/logs/alerts.md
```

---

## ✅ 配置检查清单

- [ ] Bot Token 已配置
- [ ] Chat ID 已保存（`.telegram-chat-id`）
- [ ] 测试消息已发送并收到
- [ ] 健康检查脚本已集成告警
- [ ] API 监控脚本已集成告警
- [ ] Crontab 任务运行正常
- [ ] 告警阈值已确认

---

## 🎉 配置完成后...

你会在以下情况收到 Telegram 告警：

1. **Gateway 故障** - 进程停止、端口异常、API 无响应
2. **API 问题** - Key 无效、额度用完、连接失败
3. **资源告警** - 磁盘满、内存不足
4. **Bot 离线** - Telegram Bot 无法连接

**告警会包含：**
- 🔴 告警级别
- 🕐 发生时间
- 📝 详细说明
- 💡 建议操作

---

_现在，无论你在哪里，服务器有异常都会第一时间通知你！_ 🐣📱🛡️

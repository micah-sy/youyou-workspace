# 主动意图识别配置

**版本：** v1.0  
**更新：** 2026-03-01

---

## 🎯 功能说明

`intent-monitor.py` 自动识别用户意图，包括：

| 意图类型 | 触发词 | 处理 |
|---------|--------|------|
| **reminder** | 记得、提醒我、别忘了 | 添加到待办 |
| **task** | 帮我、去做、配置 | 添加到待办 |
| **preference** | 我喜欢、我讨厌、优先 | 更新偏好文件 |
| **question** | 为什么、怎么、如何 | 详细回答 |
| **emotional** | 谢谢、开心、难过 | 记录情感记忆 |

---

## 🔧 使用方法

### 命令行

```bash
python3 scripts/intent-monitor.py "用户消息"
```

### 示例

```bash
# 提醒类
python3 scripts/intent-monitor.py "记得提醒我明天带伞"
# 输出：🎯 检测到的意图：reminder

# 任务类
python3 scripts/intent-monitor.py "帮我配置阿里云监控"
# 输出：🎯 检测到的意图：task
#      📋 提取任务：配置阿里云监控

# 情感类
python3 scripts/intent-monitor.py "太好了，谢谢你悠悠！"
# 输出：💝 情感分析：positive (强度：2)
#      😊 积极情感事件，记录中...
```

---

## 📊 输出格式

```json
{
  "intents": ["reminder", "task"],
  "emotion": "positive",
  "emotion_intensity": 2,
  "task": "配置阿里云监控",
  "timestamp": "2026-03-01T09:40:00"
}
```

---

## 🔄 集成到对话流程

### 方案 1：Heartbeat 集成

在 heartbeat 时检查最近消息：

```bash
# 添加到 HEARTBEAT.md
检查最近对话，运行 intent-monitor.py 识别意图
```

### 方案 2：消息预处理

在回复用户前，先运行意图识别：

```python
# 伪代码
message = get_user_message()
intent = run_intent_monitor(message)

if intent["task"]:
    add_to_pending_tasks(intent["task"])
elif intent["emotion"] == "positive":
    log_emotional_event(message, intent["emotion"])
```

### 方案 3：Cron 定时检查

```bash
# 每 5 分钟检查最近对话
*/5 * * * * python3 /home/admin/.openclaw/workspace/scripts/intent-monitor.py --check-recent
```

---

## 📝 自动更新的文件

| 文件 | 触发条件 | 更新内容 |
|------|---------|---------|
| `context/pending-tasks.md` | task/reminder 意图 | 添加待办任务 |
| `YYYY-MM-DD.md` | emotional 意图 | 记录情感事件 |
| `preferences/user-preferences.md` | preference 意图 | 更新用户偏好 |

---

## 🎯 意图识别规则

### reminder（提醒）

```python
patterns = [
    r"记得.*",
    r"提醒我.*",
    r"别忘了.*",
    r"待会.*",
    r"等下.*",
]
```

### task（任务）

```python
patterns = [
    r"帮我.*",
    r"去做.*",
    r"去查.*",
    r"配置.*",
    r"设置.*",
]
```

### preference（偏好）

```python
patterns = [
    r"我喜欢.*",
    r"我讨厌.*",
    r"以后.*",
    r"总是.*",
    r"优先.*",
]
```

### emotional（情感）

```python
positive_words = ["好", "棒", "赞", "开心", "喜欢", "谢谢"]
negative_words = ["不好", "差", "讨厌", "生气", "难过"]
```

---

## 💡 增强建议

### 1. LLM 增强

用 LLM 替代规则匹配：

```python
# 伪代码
prompt = f"""
分析这句话的意图：
"{message}"

意图类型：reminder/task/preference/question/emotional/chat
提取任务：如果有
情感倾向：positive/negative/neutral
"""
```

### 2. 上下文理解

考虑对话历史：

```python
# 检查前几条消息
recent_messages = get_recent_messages(limit=5)
context = "\n".join(recent_messages)
intent = analyze_with_context(context, current_message)
```

### 3. 主动建议

识别意图后主动建议：

```
检测到"记得提醒我" → 
"好的，我记下了！需要我什么时候提醒你？⏰"

检测到"帮我配置" → 
"没问题！我现在就帮你配置～🔧"

检测到"谢谢" → 
"不客气～能帮到你我很开心！🐣"
```

---

## 📊 效果评估

### 准确率测试

```bash
# 测试集
test_messages = [
    ("记得带伞", "reminder"),
    ("帮我查天气", "task"),
    ("我喜欢晴天", "preference"),
    ("为什么下雨", "question"),
    ("太好了", "emotional"),
]

# 计算准确率
accuracy = correct_predictions / total_tests
```

### 性能指标

| 指标 | 目标 | 当前 |
|------|------|------|
| 响应时间 | <100ms | ✅ ~50ms |
| 意图准确率 | >85% | 📊 待测试 |
| 任务提取率 | >70% | 📊 待测试 |

---

## 🔗 相关文件

- [[../context/pending-tasks]] - 待办任务
- [[../preferences/user-preferences]] - 用户偏好
- [[../ARCHITECTURE#主动意图理解]] - 架构文档

---

_让悠悠更懂你，从理解每一句话的意图开始。_ 🧠💝

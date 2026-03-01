#!/usr/bin/env python3
# intent-monitor.py - 主动意图识别监控
# 用法：python3 scripts/intent-monitor.py "用户消息"

import sys
import json
import re
from datetime import datetime
from pathlib import Path

# 配置
MEMORY_DIR = Path("/home/admin/.openclaw/workspace/memory")
PENDING_TASKS = MEMORY_DIR / "context" / "pending-tasks.md"
DAILY_LOG = MEMORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"

# 意图模式匹配
INTENT_PATTERNS = {
    "reminder": [
        r"记得.*",
        r"提醒我.*",
        r"别忘了.*",
        r"待会.*",
        r"等下.*",
        r"一会儿.*",
    ],
    "task": [
        r"帮我.*",
        r"去做.*",
        r"去查.*",
        r"去看看.*",
        r"配置.*",
        r"设置.*",
        r"创建.*",
    ],
    "preference": [
        r"我喜欢.*",
        r"我讨厌.*",
        r"我不喜欢.*",
        r"以后.*",
        r"总是.*",
        r"优先.*",
    ],
    "question": [
        r"为什么.*",
        r"怎么.*",
        r"如何.*",
        r"是什么.*",
        r"能.*吗",
    ],
    "emotional": [
        r"谢谢.*",
        r"感谢.*",
        r"太好了.*",
        r"开心.*",
        r"难过.*",
        r"生气.*",
    ],
}

# 情感分析关键词
POSITIVE_WORDS = ["好", "棒", "赞", "开心", "喜欢", "谢谢", "感谢", "满意", "完美"]
NEGATIVE_WORDS = ["不好", "差", "讨厌", "生气", "难过", "失望", "糟糕", "烦"]

def detect_intent(message):
    """检测用户意图"""
    intents = []
    
    for intent_type, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, message):
                intents.append(intent_type)
                break
    
    return intents if intents else ["chat"]

def analyze_emotion(message):
    """分析情感倾向"""
    positive_count = sum(1 for word in POSITIVE_WORDS if word in message)
    negative_count = sum(1 for word in NEGATIVE_WORDS if word in message)
    
    if positive_count > negative_count:
        return "positive", positive_count
    elif negative_count > positive_count:
        return "negative", negative_count
    else:
        return "neutral", 0

def extract_task(message):
    """从消息中提取任务"""
    # 简单实现，可以用 LLM 增强
    task_keywords = ["帮我", "去做", "去查", "配置", "设置", "创建"]
    
    for keyword in task_keywords:
        if keyword in message:
            task_start = message.find(keyword) + len(keyword)
            task = message[task_start:].strip()
            # 去除句末标点
            task = re.sub(r'[。！？.!?\n]+$', '', task)
            return task
    
    return None

def add_to_pending_tasks(task, priority="🟡"):
    """添加到待办任务"""
    if not PENDING_TASKS.exists():
        return False
    
    content = PENDING_TASKS.read_text(encoding='utf-8')
    
    # 找到"待处理"部分
    pending_marker = "## 📋 待处理"
    if pending_marker not in content:
        return False
    
    # 插入新任务
    lines = content.split('\n')
    new_line = f"| {task} | {priority} | 自动识别 |"
    
    for i, line in enumerate(lines):
        if line.startswith(pending_marker):
            # 找到表格开始位置
            for j in range(i+1, len(lines)):
                if lines[j].startswith('|------'):
                    lines.insert(j+1, new_line)
                    break
            break
    
    PENDING_TASKS.write_text('\n'.join(lines), encoding='utf-8')
    return True

def log_emotional_event(message, emotion, intensity):
    """记录情感事件到日志"""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_log = MEMORY_DIR / f"{today}.md"
    
    timestamp = datetime.now().strftime('%H:%M')
    
    log_entry = f"""
### {timestamp} — 情感事件 {emotion}

**强度：** {intensity}
**内容：** {message}

**处理：** 已记录到情感记忆，半衰期 347 天

"""
    
    if daily_log.exists():
        content = daily_log.read_text(encoding='utf-8')
        content += log_entry
        daily_log.write_text(content, encoding='utf-8')
    else:
        daily_log.write_text(f"# {today}\n\n{log_entry}", encoding='utf-8')

def main():
    if len(sys.argv) < 2:
        print("用法：python3 intent-monitor.py \"用户消息\"")
        sys.exit(1)
    
    message = sys.argv[1]
    
    # 检测意图
    intents = detect_intent(message)
    print(f"🎯 检测到的意图：{', '.join(intents)}")
    
    # 分析情感
    emotion, intensity = analyze_emotion(message)
    print(f"💝 情感分析：{emotion} (强度：{intensity})")
    
    # 提取任务
    if "task" in intents or "reminder" in intents:
        task = extract_task(message)
        if task:
            print(f"📋 提取任务：{task}")
            if add_to_pending_tasks(task):
                print("✅ 已添加到待办任务")
            else:
                print("⚠️ 添加失败（手动添加）")
    
    # 记录情感事件
    if emotion == "positive" and intensity > 0:
        print("😊 积极情感事件，记录中...")
        log_emotional_event(message, emotion, intensity)
    
    # 输出 JSON（供其他脚本使用）
    result = {
        "intents": intents,
        "emotion": emotion,
        "emotion_intensity": intensity,
        "task": extract_task(message) if ("task" in intents) else None,
        "timestamp": datetime.now().isoformat(),
    }
    print(f"\n📊 JSON 输出：{json.dumps(result, ensure_ascii=False)}")

if __name__ == "__main__":
    main()

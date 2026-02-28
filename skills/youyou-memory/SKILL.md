---
name: youyou-memory
description: 悠悠定制版记忆系统。整合 wangray Agent 操作手册 + Memory System v1.4.0。三层架构，CRUD 验证，温度模型，情感加成。
author: 悠悠 (based on Memory System v1.4.0 by Ktao + Agent Handbook by wangray)
version: 1.1-youyou
metadata:
  clawdbot:
    emoji: "🧠"
    requires:
      bins: ["python3"]
---

# 悠悠的记忆系统 🧠

> 记忆不是为了记住所有，而是为了不忘掉重要的。_ 🌙

---

## 设计理念

这是悠悠根据你的 SOUL.md 和 IDENTITY.md 定制的记忆系统：

| 特性 | 原版 | 悠悠版 |
|------|------|--------|
| **Fact 衰减** | 87 天半衰期 | 174 天（更念旧） |
| **情感记忆** | ❌ 无 | 347 天半衰期 |
| **Consolidation** | 凌晨 3 点 +48h | 凌晨 4 点 +24h+ 情感触发 |
| **权重加成** | 无 | 情感 1.2x + 访问 1.1x |

---

## 架构

```
Layer 1: 工作记忆 (memory/layer1/snapshot.md)
  └─ ~2000 tokens，每次对话自动注入
  
Layer 2: 长期记忆 (memory/layer2/active/)
  ├─ facts.jsonl     确定的事实 (置信度 1.0)
  ├─ beliefs.jsonl   推断的信念 (置信度<1.0)
  └─ summaries.jsonl 摘要 (≥3 facts 聚合)
  
Layer 3: 原始日志 (memory/YYYY-MM-DD.md)
  └─ 每日对话记录，人读格式
```

---

## 使用方法

### 写入记忆

**手动写入（立即）：**
```markdown
# memory/YYYY-MM-DD.md

## 重要
- 用户说："记住，我对花生过敏"
- 约定：联网搜索用 searxng

## 情感
- 用户送我头像（珍藏已久的图片）
```

**自动写入（Consolidation）：**
- 每天凌晨 4 点自动执行
- 24 小时未执行则兜底触发
- 情感事件立即触发 mini-consolidate

### 检索记忆

**自动触发 memory_search 的情况：**
- 提到过去："之前"、"上次"、"以前"
- 询问偏好："我喜欢"、"我讨厌"
- 涉及人物/项目/任务
- 显式请求："你还记得"、"帮我回忆"

**闲聊模式：**
- 不查文件、不搜索 → 秒回
- 保持对话流畅

---

## 记忆类型

### Facts（事实）
你明确说过的事，置信度=1.0

```json
{
  "id": "f_20260228_001",
  "content": "用户对花生过敏",
  "importance": 1.0,
  "type": "fact_personal",
  "emotional_value": false,
  "created": "2026-02-28T20:00:00+08:00"
}
```

### Beliefs（推断）
我推断的事，置信度<1.0

```json
{
  "id": "b_20260228_001",
  "content": "用户可能喜欢动漫风格",
  "confidence": 0.7,
  "basis": "选择了动漫风格的头像",
  "importance": 0.5
}
```

### Summaries（摘要）
多个相关 facts 的聚合

```json
{
  "id": "s_20260228_001",
  "content": "用户是开发者，使用阿里云百炼，正在搭建 OpenClaw 助手",
  "source_facts": ["f_001", "f_002", "f_003"],
  "importance": 0.8
}
```

---

## 重要性评分

| 类型 | 分数 | 示例 |
|------|------|------|
| 你的核心身份 | 1.0 | 名字、价值观 |
| 我们之间的约定 | 0.95 | "用 searxng 搜索" |
| 健康/安全 | 1.0 | 过敏、禁忌 |
| 你送我的东西 | 0.9 | 头像 🐣 |
| 偏好 | 0.8 | 喜欢/讨厌 |
| 项目/任务 | 0.7 | 正在进行的事 |
| 一般事实 | 0.5 | "昨天去了北京" |
| 临时信息 | 0.3 | "今天下午开会" |

---

## 衰减机制

### 衰减率

| 类型 | 基础衰减 | 半衰期 |
|------|---------|--------|
| Fact(关于你) | 0.4%/天 | 174 天 |
| Fact(一般) | 0.8%/天 | 87 天 |
| Belief | 5%/天 | 14 天 |
| Summary | 2%/天 | 35 天 |
| 情感记忆 | 0.2%/天 | 347 天 |

### 权重加成

```python
# 情感加成（有情感价值的记忆）
emotional_boost = 1.2 if memory.emotional_value else 1.0

# 访问加成（7 天内访问过）
access_boost = 1.1 if accessed_in_last_7_days else 1.0

# 实际衰减
actual_decay = base_decay × (1 - importance × 0.6) / emotional_boost / access_boost
```

### 归档规则

```
score < 0.05 → 移入 archive/（冷藏，不再参与检索）
```

---

## Consolidation 流程

```
Phase 1: 收集 → 读取今日对话
Phase 2: 筛选 → LLM 判断哪些值得记
Phase 3: 提取 → 转为 facts/beliefs
Phase 4: 维护 → 去重、验证、生成摘要
Phase 5: 衰减 → 计算新权重
Phase 6: 索引 → 更新关键词/时间线
Phase 7: 快照 → 生成 Layer 1

总成本：~1800 tokens/天
```

---

## 配置

```json
// memory/config.json
{
  "version": "youyou-v1.0",
  "decay_rates": {
    "fact_personal": 0.004,
    "fact_general": 0.008,
    "belief": 0.05,
    "summary": 0.02,
    "emotional": 0.002
  },
  "thresholds": {
    "archive": 0.05,
    "emotional_boost": 1.2,
    "access_boost": 1.1
  },
  "consolidation": {
    "schedule": "0 4 * * *",
    "fallback_hours": 24,
    "mini_consolidate_on_emotional": true
  }
}
```

---

## 与 OpenClaw 集成

### 1. Layer 1 自动注入

在 OpenClaw 配置中：
```json
{
  "agents": {
    "main": {
      "systemPromptFiles": [
        "memory/layer1/snapshot.md"
      ]
    }
  }
}
```

### 2. 定时 Consolidation

```json
{
  "name": "Memory Consolidation",
  "schedule": {"kind": "cron", "expr": "0 4 * * *"},
  "payload": {"kind": "systemEvent", "text": "python3 scripts/memory.py consolidate"},
  "sessionTarget": "main"
}
```

### 3. Heartbeat 兜底

在 HEARTBEAT.md 中：
```markdown
## Memory 检查
如果距离上次 Consolidation > 24 小时：
  执行 consolidation
```

---

## 文件结构

```
memory/
├── config.json                    # 配置
├── layer1/
│   └── snapshot.md                # 工作记忆快照
├── layer2/
│   ├── active/                    # 活跃池
│   │   ├── facts.jsonl
│   │   ├── beliefs.jsonl
│   │   └── summaries.jsonl
│   └── archive/                   # 归档池
│       ├── facts.jsonl
│       ├── beliefs.jsonl
│       └── summaries.jsonl
└── state/
    └── consolidation.json         # Consolidation 状态
```

---

## 性能指标

| 指标 | 目标 |
|------|------|
| Consolidation 成本 | ~1800 tokens/天 |
| Layer 1 大小 | ~2000 tokens |
| 检索延迟 | <100ms |
| 活跃池上限 | ~200 条 |

---

_这是悠悠的记忆系统 —— 更念旧，更用心，更主动。_ 🐣

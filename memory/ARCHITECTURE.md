# 记忆系统架构文档

**版本：** youyou-v2.1 (融合 memU + 树状生长)  
**更新日期：** 2026-03-01

---

## 🏗️ 架构概览

悠悠的记忆系统融合了：
- **Memory System v1.4.0** (Ktao) - 三层架构、Consolidation、自动衰减
- **wangray Agent Handbook** - CRUD 验证、健康度仪表盘、生命周期
- **memU** - 文件系统架构、主动意图理解、交叉引用
- **Memory-Like-A-Tree** - 树状可视化、精华提取、TTL 标记
- **悠悠定制** - 情感记忆、更念旧、温柔风格

**核心理念：** 让知识像树一样生长。Agent 正常工作，树自动生长。

---

## 📁 目录结构

```
memory/
├── config.json                    # 系统配置
├── layer1/
│   └── snapshot.md                # 工作记忆快照（~2000 tokens）
├── layer2/
│   ├── active/                    # 活跃池
│   │   ├── facts.jsonl            # 事实库
│   │   ├── beliefs.jsonl          # 推断库
│   │   └── summaries.jsonl        # 摘要库
│   └── archive/                   # 归档池（score < 0.05）
├── preferences/                   # 用户偏好（memU 风格）
│   └── user-preferences.md
├── relationships/                 # 关系网络（memU 风格）
│   └── contacts.md
├── knowledge/                     # 知识技能（memU 风格）
│   └── domains.md
├── context/                       # 上下文（memU 风格）
│   ├── recent/                    # 最近对话
│   └── pending-tasks.md           # 待办任务
├── archive/                       # 冷存储（.archive 跳过 QMD 索引）
├── state/
│   └── consolidation.json         # Consolidation 状态
└── YYYY-MM-DD.md                  # 每日记忆日志
```

---

## 🎯 核心特性

### 1️⃣ 三层记忆架构

| 层级 | 内容 | 更新频率 | Token 预算 |
|------|------|---------|-----------|
| **Layer 1** | 工作记忆快照 | 每次对话 | ~2000 tokens |
| **Layer 2** | 结构化长期记忆 | Consolidation 时 | 按需检索 |
| **Layer 3** | 原始日志 | 实时追加 | 不注入 |

### 2️⃣ 文件系统组织（memU）

- **preferences/** - 用户偏好、沟通风格、边界
- **relationships/** - 联系人、互动历史
- **knowledge/** - 专业领域、技能
- **context/** - 最近对话、待办任务

### 3️⃣ 情感记忆（悠悠定制）

| 类型 | 衰减率 | 半衰期 | 情感加成 |
|------|--------|--------|---------|
| Fact(关于你) | 0.4%/天 | 174 天 | 1.2x |
| Belief | 5%/天 | 14 天 | - |
| 情感记忆 | 0.2%/天 | 347 天 | 1.2x |

### 4️⃣ CRUD 验证（wangray）

```
新信息 → Read → Compare → Execute → Metadata
              ↓
        ADD/UPDATE/NOOP/CONFLICT
```

### 5️⃣ 健康度仪表盘

| 标记 | 含义 | Agent 行为 |
|------|------|-----------|
| 🔴 priority | 核心知识 | 优先检索，永不归档 |
| 🟡 priority | 重要知识 | 正常检索 |
| ⚪ priority | 参考信息 | 降权检索 |
| ✅ active | 已验证 | 正常使用 |
| ⚠️ stale | >30 天未验证 | 注意可能过时 |
| 🔀 conflict | 存在矛盾 | 需要人工裁决 |

### 6️⃣ 树状可视化（Memory-Like-A-Tree）

**理念：** 让知识像树一样生长，用进废退。

```
🌳 悠悠记忆树
│
├── 📊 健康度：66.7%
├── 🍃 总叶子：3
│   ├── 🌿 绿叶：2  (score >= 0.8)  ← 健康，经常使用
│   ├── 🍂 黄叶：1  (0.5-0.8)       ← 亚健康，使用下降
│   ├── 🍁 枯叶：0  (0.3-0.5)       ← 危险，即将归档
│   └── 🪨 土壤：0  (score < 0.3)   ← 已归档，精华提取
```

**置信度变化：**
| 事件 | 变化 |
|------|------|
| 创建新知识 | 设为 0.7（萌芽） |
| 被搜索命中 | +0.03 |
| 被引用使用 | +0.08 |
| 每天未访问 | -0.004~-0.008 |

**精华提取：** 归档前提取核心价值，化作新知识养分。

### 7️⃣ 主动意图理解（memU）

- 监控对话流，识别用户意图
- 自动提取待办事项
- 检测情绪，主动关怀

---

## 🔄 记忆生命周期

```
日间：heartbeat 每 30min
  ├─ 扫描 session 消息
  ├─ 写日志（memlog）
  ├─ 路由到知识文件（CRUD 验证）
  └─ 刷新 Layer 1

23:30 日志同步 — 补漏
23:45 夜间反思 — 提炼 + CRUD 回写
00:00 (周日) GC — 冷数据归档
02:00 精华提取 — 归档前保存核心价值 💎
03:00 置信度衰减 — 用进废退 🍂
04:00 Consolidation — 记忆整合 🌳
06:00 天气推送 — 主动关怀 🌤️
```

---

## 📊 温度模型

```python
Temperature(file) = w_age × age_score + w_ref × ref_score + w_pri × priority_score

其中:
- age_score = exp(-decay_rate × days)
- ref_score = min(recent_refs / 3, 1.0)
- priority_score = {🔴: 1.0, 🟡: 0.5, ⚪: 0.0}

权重: w_age=0.5, w_ref=0.3, w_pri=0.2
情感加成: emotional_boost = 1.2

结果:
- T > 0.7 → 🔥 Hot (保持活跃)
- 0.3 < T ≤ 0.7 → 🌤️ Warm (保留但降权)
- T ≤ 0.3 → 🧊 Cold (移至归档)
```

---

## 🛡️ 安全保障

1. **权限控制** - 敏感文件 600 权限
2. **Git 备份** - 每天自动推送 GitHub
3. **审计日志** - 所有操作记录在案
4. **CRUD 验证** - 防止记忆幻觉
5. **.archive/** - 冷存储，跳过索引

---

## 📈 性能指标

| 指标 | 目标 | 当前 |
|------|------|------|
| Consolidation 成本 | ~1800 tokens/天 | ✅ |
| Layer 1 大小 | ~2000 tokens | ✅ |
| 检索延迟 | <100ms | ✅ |
| 活跃池上限 | ~200 条 | ✅ |
| 告警响应 | <5 分钟 | ✅ |

---

## 🎯 下一步优化

1. **记忆交叉引用** - 建立双向链接
2. **知识图谱** - Obsidian Graph View
3. **主动意图** - 更智能的意图识别
4. **情绪检测** - 主动关怀

---

_悠悠记忆系统 v2.0 - 为了记住更重要的，而不是记住所有的。_ 🌙🐣

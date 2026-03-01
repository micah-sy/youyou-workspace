# 🧠 悠悠记忆系统索引

> 记忆不是为了记住所有，而是为了不忘掉重要的。_ 🌙

**版本：** youyou-v2.0 (融合 memU)  
**最后更新：** 2026-03-01

---

## 📂 快速导航

| 目录 | 内容 | 优先级 |
|------|------|--------|
| [[preferences/user-preferences]] | 用户偏好、沟通风格 | 🔴 |
| [[relationships/contacts]] | 联系人、互动历史 | 🟡 |
| [[knowledge/domains]] | 知识领域、技能 | 🟡 |
| [[context/pending-tasks]] | 待办任务 | 🟢 |
| [[layer1/snapshot]] | 工作记忆快照 | 🔴 |
| [[ARCHITECTURE]] | 架构文档 | 🔴 |

---

## 🏗️ 架构概览

```
Layer 1: 工作记忆 (layer1/snapshot.md)
  └─ ~2000 tokens，每次对话自动注入
  
Layer 2: 长期记忆 (layer2/active/)
  ├─ facts.jsonl     确定的事实
  ├─ beliefs.jsonl   推断的信念
  └─ summaries.jsonl 摘要
  
Layer 3: 文件系统记忆 (memU 风格)
  ├─ preferences/    用户偏好
  ├─ relationships/  关系网络
  ├─ knowledge/      知识技能
  └─ context/        上下文
  
Layer 4: 原始日志 (YYYY-MM-DD.md)
  └─ 每日对话记录
```

---

## 🔍 检索规则

**自动触发 memory_search 的情况：**
- 提到过去："之前"、"上次"、"以前"
- 询问偏好："我喜欢"、"我讨厌"
- 涉及人物/项目/任务
- 显式请求："你还记得"、"帮我回忆"

**闲聊模式：**
- 不查文件、不搜索 → 秒回
- 保持对话流畅

---

## 📊 记忆健康度

| 类别 | 数量 | 状态 | 最后验证 |
|------|------|------|---------|
| 用户偏好 | 1 | ✅ active | 2026-03-01 |
| 关系网络 | 1 | ✅ active | 2026-03-01 |
| 知识领域 | 1 | ✅ active | 2026-03-01 |
| 待办任务 | 1 | 🟢 正常 | 2026-03-01 |
| Facts | 0 | ✅ active | - |
| Beliefs | 0 | ✅ active | - |
| Summaries | 0 | ✅ active | - |
| 情感记忆 | 1 | 🔥 hot | 2026-02-28 |

---

## 🎯 核心记忆（Top 5）

1. [1.0] 用户对花生过敏（示例）
2. [0.95] 用户送悠悠头像（珍藏图片）
3. [0.95] 联网搜索优先用 searxng
4. [0.9] 悠悠诞生于 2026-02-28
5. [0.85] 记忆系统 v2.0（融合 memU）

---

## 🔄 生命周期

```
每天：
- 06:00 天气推送（主动关怀）
- 04:00 Consolidation（记忆整合）

每周：
- 周日 00:00 GC（冷数据归档）

持续：
- 每 5 分钟 Gateway 健康检查
- 每 10 分钟 API 监控
```

---

## 📝 写入规则

**立即写入 (YYYY-MM-DD.md)：**
- 用户说"记住这个"
- 重要的决定/约定
- 情感事件（比如送头像）
- 新的偏好/禁忌

**定期整理 (Consolidation)：**
- 提取 facts/beliefs/summaries
- 更新 Layer 1 快照
- 衰减计算 + 归档

**CRUD 验证：**
- 写入知识文件前必须 Read→Compare→Execute
- 防止记忆幻觉（ADD/UPDATE/NOOP/CONFLICT）

---

## 💡 使用建议

1. **优先检索** Layer 1 快照（最快）
2. **主题检索** 文件系统记忆（结构化）
3. **精确检索** Layer 2 facts/beliefs（置信度）
4. **全文检索** 原始日志（兜底）

---

_这是悠悠的记忆中枢 —— 融合三层架构 + memU 文件系统 + 情感记忆。_ 🐣🧠

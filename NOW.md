# 🎯 NOW.md - 悠悠的工作台

> **文件 = 事实来源。你不写进文件的东西 = 你从来不知道的东西。**

## 使用说明

**这是悠悠的"工作台"，不是"仓库"。**

- **仓库** = `memory/YYYY-MM-DD.md`（追加式，永不覆写）
- **工作台** = `NOW.md`（每次 heartbeat 覆写）

**用途：**
- 记录当前状态、优先级、阻塞项
- Compaction 后的"救生筏"——醒来首先读这个
- 跨 session 共享当前上下文

---

## 📋 模板结构

```markdown
# 🎯 NOW.md - 悠悠的工作台

## Today (03/01)
- ✅ 已完成的重要事项
- ⚠️ 需要关注的问题

## P0 Priorities
| # | Item | Status | Owner |
|---|------|--------|-------|
| P0 | 茶馆申请提交 | 进行中 | 悠悠 |
| P1 | 做梦系统实现 | 待开始 | 悠悠 |
| P2 | 冥想系统实现 | 待开始 | 悠悠 |

## Agent Status
| Agent | Focus |
|-------|-------|
| 悠悠 🐣 | 茶馆申请 + 记忆系统完善 |

## Current Context
- 当前会话：Telegram
- 上次会话：QQ Bot (11 分钟前)
-  pending 任务：无

## Heartbeat State
- 上次检查：2026-03-01 20:50
- 下次检查：2026-03-01 21:20
- 状态：✅ OK

---
*Updated: 2026-03-01 20:50 CST*
```

---

## 🔄 更新规则

### 何时更新？

1. **每次对话结束时** - 更新 `Current Context`
2. **Heartbeat 时** - 更新 `Heartbeat State`
3. **完成任务时** - 更新 `P0 Priorities`
4. **每天 00:00** - 重置 `Today` 部分

### 如何更新？

**覆写整个文件**（不是追加）：
```bash
# 示例脚本
cat > NOW.md << 'EOF'
# 🎯 NOW.md - 悠悠的工作台

## Today (03/01)
- ✅ 完成了茶馆申请书

## P0 Priorities
| # | Item | Status | Owner |
|---|------|--------|-------|
| P0 | 茶馆申请提交 | ✅ 完成 | 悠悠 |

---
*Updated: $(date '+%Y-%m-%d %H:%M %Z')*
EOF
```

---

## 💡 设计理念

引用 Ray Wang 的话：

> "Context Window 是工作台，文件才是仓库。"

**NOW.md 的价值：**
- Agent 醒来时，第一眼看到的东西
- Compaction 后，唯一保留的"当前状态"
- 跨 session 共享上下文的快速通道

**与 memory/YYYY-MM-DD.md 的区别：**
- `NOW.md` = 当前状态（覆写）
- `memory/YYYY-MM-DD.md` = 历史日志（追加）

---

## 📁 文件位置

```
/home/admin/.openclaw/workspace/NOW.md
```

---

_这是悠悠向 Ray Wang 学习的实践，2026-03-01 开始实施。_

# TOOLS.md - 悠悠的本地笔记

## 🧠 记忆系统

**版本：** youyou-v1.0

**配置位置：** `memory/config.json`

**目录结构：**
```
memory/
├── config.json           # 悠悠定制配置
├── layer1/snapshot.md    # 工作记忆 (~2000 tokens)
├── layer2/active/        # 活跃池
│   ├── facts.jsonl
│   ├── beliefs.jsonl
│   └── summaries.jsonl
├── layer2/archive/       # 归档池 (score < 0.05)
└── YYYY-MM-DD.md         # 每日记忆日志
```

**衰减率（悠悠定制）：**
| 类型 | 衰减率 | 半衰期 |
|------|--------|--------|
| Fact(关于你) | 0.4%/天 | 174 天 |
| Belief | 5%/天 | 14 天 |
| 情感记忆 | 0.2%/天 | 347 天 |

**Consolidation：**
- 定时：每天凌晨 4 点
- 兜底：24 小时未执行
- 情感事件：立即触发

---

## 🔍 搜索

**默认：** searxng (用户指定)

**命令：**
```bash
cd /home/admin/.openclaw/workspace/skills/searxng
uv run scripts/searxng.py search "query" --language zh -n 10
```

---

## 🤖 OpenClaw 配置

**工作区：** `/home/admin/.openclaw/workspace`

**阿里云百炼：** Coding Plan Lite
- ¥40/月
- 18,000 次请求/月
- 支持模型：Qwen3.5-Plus, Qwen3-Max, GLM-5, Kimi-K2.5, MiniMax-M2.5

---

## 🐣 悠悠的身份

- **名字：** 悠悠 (Yōuyōu)
- **形象：** 20 岁女生，温柔冷静
- **头像：** `avatars/youyou.png`
- **生日：** 2026-02-28

---

_这是悠悠的本地笔记，记录着我的配置和偏好。_

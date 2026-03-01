# 悠悠记忆树自动化配置

**版本：** youyou-v2.1  
**设置日期：** 2026-03-01

---

## 🕐 Cron 任务配置

让记忆树自动生长，只需设置一次 Cron：

```bash
crontab -e
```

### 添加以下任务：

```cron
# ═══════════════════════════════════════════════════════════
# 悠悠记忆树自动化 (Youyou Memory Tree Automation)
# ═══════════════════════════════════════════════════════════

# 每天凌晨 2 点：精华提取（归档前保存核心价值）
0 2 * * * cd /home/admin/.openclaw/workspace && python3 scripts/essence-extractor.py --quiet

# 每天凌晨 3 点：置信度衰减（用进废退）
0 3 * * * cd /home/admin/.openclaw/workspace && python3 scripts/memory-tree.py --quiet

# 每天凌晨 4 点：记忆 Consolidation（已有任务）
0 4 * * * cd /home/admin/.openclaw/workspace && python3 scripts/consolidation.py --quiet

# 每 2 小时：记忆树健康度检查（可选）
0 */2 * * * cd /home/admin/.openclaw/workspace && python3 scripts/memory-tree.py --quiet --output memory/tree-report.md

# 每天早上 8 点：生成记忆树日报（可选）
0 8 * * * cd /home/admin/.openclaw/workspace && python3 scripts/memory-tree.py --output memory/reports/tree-$(date +\%Y\%m\%d).md
```

---

## 📊 手动命令

### 查看记忆树状态

```bash
cd /home/admin/.openclaw/workspace
python3 scripts/memory-tree.py
```

### 生成详细报告

```bash
python3 scripts/memory-tree.py --output memory/tree-report.md
```

### 精华提取（预览模式）

```bash
python3 scripts/essence-extractor.py --dry-run
```

### 精华提取（执行）

```bash
python3 scripts/essence-extractor.py
```

---

## 🌳 树的生长流程

```
1. Agent 对话 → 新记忆创建 (置信度 0.7)
              ↓
2. 被使用/搜索 → 置信度 ↑ (+0.03~0.08)
              ↓
3. 🌿 绿叶 (>=0.8) ← 健康状态
              ↓
4. 长期不用 → 置信度 ↓ (-0.004~-0.008/天)
              ↓
5. 🍂 黄叶 (0.5-0.8) ← 亚健康
              ↓
6. 继续不用 → 置信度继续 ↓
              ↓
7. 🍁 枯叶 (0.3-0.5) ← 危险
              ↓
8. 置信度 < 0.3 → 精华提取 💎
              ↓
9. 🪨 土壤 (归档) → 精华可被新知识引用
```

---

## 📈 健康度指标

| 健康度 | 状态 | 建议 |
|--------|------|------|
| >= 80% | 🟢 优秀 | 继续保持 |
| 70-80% | 🟡 良好 | 正常 |
| 50-70% | 🟠 一般 | 增加记忆使用 |
| < 50% | 🔴 需关注 | 检查记忆系统 |

---

## 💡 最佳实践

1. **每天查看一次记忆树** - 了解记忆健康状态
2. **定期搜索旧记忆** - 提升置信度，防止归档
3. **关注黄叶记忆** - 及时使用或决定归档
4. **查看精华文件** - `memory/essence.jsonl` 包含归档前的智慧

---

_让知识像树一样生长。_ 🌳

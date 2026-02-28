# 悠悠的 Cron 任务配置

## 定期备份
每天凌晨 5 点自动备份工作区（Consolidation 完成后）

```bash
# 添加到 crontab: crontab -e
0 5 * * * /home/admin/.openclaw/workspace/scripts/backup.sh "Daily backup - $(date +\%Y-\%m-\%d)"
```

## 记忆 Consolidation
每天凌晨 4 点执行记忆整合

```bash
# 通过 OpenClaw cron 配置（在 openclaw.json 中）
{
  "name": "Memory Consolidation",
  "schedule": {"kind": "cron", "expr": "0 4 * * *"},
  "payload": {"kind": "systemEvent", "text": "python3 /home/admin/.openclaw/workspace/skills/youyou-memory/scripts/memory.py consolidate"}
}
```

## 每周 GC 归档
每周日凌晨 0 点执行冷数据归档

```bash
# 添加到 crontab
0 0 * * 0 /home/admin/.openclaw/workspace/scripts/memory-gc.sh
```

---

_最后更新：2026-02-28_

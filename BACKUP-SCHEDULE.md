# 🕒 悠悠备份定时任务配置

## 📋 Cron 配置

### 方式 1：使用 crontab（推荐）

```bash
# 编辑 crontab
crontab -e

# 添加以下行：
```

### 定时任务配置

```cron
# 悠悠记忆系统备份计划

# 每天凌晨 3:00 - 增量备份
0 3 * * * /home/admin/.openclaw/workspace/scripts/backup-memory.sh incremental >> /home/admin/.openclaw/logs/backup.log 2>&1

# 每周日 凌晨 2:00 - 全量备份
0 2 * * 0 /home/admin/.openclaw/workspace/scripts/backup-memory.sh full >> /home/admin/.openclaw/logs/backup.log 2>&1

# 每天凌晨 4:00 - GitHub 云同步（consolidation 后）
0 4 * * * /home/admin/.openclaw/workspace/scripts/sync-cloud.sh github >> /home/admin/.openclaw/logs/sync.log 2>&1

# 每周一 凌晨 5:00 - 阿里云 OSS 备份（可选）
0 5 * * 1 /home/admin/.openclaw/workspace/scripts/sync-cloud.sh aliyun >> /home/admin/.openclaw/logs/sync.log 2>&1
```

---

## ⏰ 备份时间表

| 时间 | 任务 | 说明 |
|------|------|------|
| **每天 03:00** | 增量备份 | 备份最近 24 小时更改 |
| **每周日 02:00** | 全量备份 | 完整备份 memory/ 目录 |
| **每天 04:00** | GitHub 同步 | consolidation 后推送 |
| **每周一 05:00** | 阿里云备份 | 云存储备份（可选） |

---

## 📊 备份策略

### 保留策略
- **本地备份**：保留最近 7 天
- **GitHub 备份**：永久（Git 历史）
- **阿里云备份**：保留最近 30 天

### 备份内容
- ✅ `memory/` - 所有记忆文件
- ✅ `NOW.md` - 工作台状态
- ✅ `EVOLUTION-PLAN.md` - 进化计划
- ✅ `scripts/` - 脚本文件
- ❌ `.git/` - 不需要（Git 仓库已包含）

---

## 🔧 手动备份

### 本地备份
```bash
# 增量备份
./scripts/backup-memory.sh incremental

# 全量备份
./scripts/backup-memory.sh full
```

### 云同步
```bash
# GitHub 同步
./scripts/sync-cloud.sh github

# 阿里云同步
./scripts/sync-cloud.sh aliyun

# 全部同步
./scripts/sync-cloud.sh all
```

---

## 📁 备份位置

| 类型 | 位置 |
|------|------|
| **本地备份** | `/home/admin/.openclaw/backups/memory/` |
| **Git 备份** | `https://github.com/micah-sy/youyou-workspace` |
| **阿里云备份** | `oss://your-bucket/memory-backup/`（需配置） |

---

## ⚠️ 恢复备份

### 从本地备份恢复
```bash
# 查看可用备份
ls -lh /home/admin/.openclaw/backups/memory/

# 恢复指定备份
cd /home/admin/.openclaw/workspace
tar -xzf /home/admin/.openclaw/backups/memory/memory-full-20260301_030000.tar.gz
```

### 从 Git 恢复
```bash
cd /home/admin/.openclaw/workspace
git log --oneline  # 查看历史
git checkout <commit-hash>  # 恢复到指定版本
git checkout main  # 回到最新版
```

---

## 📝 日志查看

```bash
# 查看备份日志
tail -f /home/admin/.openclaw/logs/backup.log

# 查看同步日志
tail -f /home/admin/.openclaw/logs/sync.log
```

---

_创建于 2026-03-01，悠悠的备份计划_

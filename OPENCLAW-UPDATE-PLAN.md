# 🔄 OpenClaw 自动更新方案

## 📊 当前状态

| 项目 | 信息 |
|------|------|
| **当前版本** | 2026.2.26 |
| **安装位置** | `/opt/openclaw/` |
| **配置位置** | `~/.openclaw/openclaw.json` |
| **更新机制** | pnpm + npm |

---

## ⚠️ 配置问题

发现配置错误：
```
plugins.allow: plugin not found: dingtalk
plugins.allow: plugin not found: wecom
```

**原因：** 之前清理扩展时删除了 DingTalk 和 WeCom，但配置中还有引用

**修复：** 需要从配置中移除这两个插件

---

## 🔄 自动更新方案

### 方案 1：手动检查更新（推荐）

```bash
# 检查最新版本
openclaw update --dry-run

# 执行更新
openclaw update
```

### 方案 2：自动检查 + 手动确认（安全）

创建一个脚本，每天检查更新并通知用户：

```bash
#!/bin/bash
# scripts/check-openclaw-update.sh

CURRENT_VERSION=$(openclaw --version)
LATEST_VERSION=$(npm view openclaw version 2>/dev/null || echo "unknown")

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
  echo "⚠️  OpenClaw 有新版本可用！"
  echo "当前版本：$CURRENT_VERSION"
  echo "最新版本：$LATEST_VERSION"
  echo ""
  echo "运行以下命令更新："
  echo "  openclaw update"
fi
```

### 方案 3：全自动更新（有风险，需备份）

```bash
#!/bin/bash
# scripts/auto-update-openclaw.sh

set -e

BACKUP_DIR="/home/admin/.openclaw/backups/openclaw"
DATE=$(date '+%Y%m%d_%H%M%S')

echo "🔄 开始自动更新 OpenClaw..."

# 1. 备份当前配置
echo "📦 备份配置..."
mkdir -p "$BACKUP_DIR"
cp -r ~/.openclaw "$BACKUP_DIR/openclaw-config-$DATE"

# 2. 检查更新
CURRENT_VERSION=$(openclaw --version)
LATEST_VERSION=$(npm view openclaw version 2>/dev/null || echo "$CURRENT_VERSION")

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
  echo "✅ 已是最新版本 ($CURRENT_VERSION)"
  exit 0
fi

echo "📊 当前版本：$CURRENT_VERSION"
echo "📊 最新版本：$LATEST_VERSION"

# 3. 执行更新
echo "🔄 执行更新..."
openclaw update

# 4. 验证更新
NEW_VERSION=$(openclaw --version)
if [ "$NEW_VERSION" = "$LATEST_VERSION" ]; then
  echo "✅ 更新成功！($NEW_VERSION)"
  
  # 保留最近 5 个备份
  ls -t "$BACKUP_DIR" | tail -n +6 | xargs -I {} rm -rf "$BACKUP_DIR/{}"
else
  echo "❌ 更新失败！当前版本：$NEW_VERSION"
  echo "🔄 尝试恢复配置..."
  rm -rf ~/.openclaw
  cp -r "$BACKUP_DIR/openclaw-config-$DATE" ~/.openclaw
  echo "✅ 已恢复到更新前状态"
fi
```

---

## 🎯 悠悠的建议

### 推荐方案：**半自动更新**

1. **每天检查** - Cron 任务检查新版本
2. **通知用户** - 通过 Telegram 通知
3. **用户确认** - 用户回复"更新"才执行
4. **自动备份** - 更新前自动备份配置
5. **失败回滚** - 更新失败自动恢复

### 不推荐：全自动更新

**原因：**
- OpenClaw 是核心系统，更新可能破坏配置
- 新版本可能不兼容现有技能
- 需要人工验证更新后的功能

---

## 📝 实施步骤

### 1. 修复当前配置问题

```bash
# 编辑配置文件，移除不存在的插件
openclaw config set plugins.allow "[]"
# 或者手动编辑 ~/.openclaw/openclaw.json
```

### 2. 创建更新检查脚本

保存为 `scripts/check-openclaw-update.sh`

### 3. 添加 Cron 任务

```bash
# 每周一上午 9 点检查更新
0 9 * * 1 /home/admin/.openclaw/workspace/scripts/check-openclaw-update.sh >> /home/admin/.openclaw/logs/update.log 2>&1
```

### 4. 测试更新流程

```bash
# 手动测试
openclaw update --dry-run
```

---

## 🔧 悠悠可以帮你

1. ✅ **创建更新检查脚本**
2. ✅ **配置 Cron 任务**
3. ✅ **修复当前配置问题**
4. ✅ **更新时通知你**（通过 Telegram）
5. ❌ **自动执行更新**（需要你的确认）

---

**你想让悠悠：**
- A. 只检查更新，通知你（推荐）
- B. 自动更新，但先备份
- C. 完全手动，悠悠不参与

请告诉我你的选择！🐣

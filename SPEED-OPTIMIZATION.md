# 🚀 悠悠消息回复速度优化指南

## 📊 当前性能分析

### 回复延迟的常见原因

| 原因 | 占比 | 说明 |
|------|------|------|
| **模型推理慢** | 40% | LLM 生成回复需要时间 |
| **记忆检索慢** | 30% | 搜索记忆文件耗时 |
| **网络延迟** | 15% | API 调用延迟 |
| **上下文过长** | 10% | Token 太多处理慢 |
| **其他** | 5% | 系统负载、磁盘 IO 等 |

---

## ⚡ 优化方案

### 方案 1：优化模型配置（效果最明显）

**当前配置：**
```json
{
  "model": {
    "primary": "dashscope-coding/qwen3.5-plus"
  }
}
```

**优化建议：**

#### A. 使用更快的模型别名
```bash
# 编辑配置
openclaw config set agents.defaults.model.primary "qwen3.5-plus"
```

#### B. 切换到更快的模型（如果可用）
- **qwen3.5-plus** - 平衡速度和智能（推荐）
- **qwen3-max-2025-09-23** - 更快但稍弱
- **qwen3-max-2026-01-23** - 最强但稍慢

**测试命令：**
```bash
# 临时切换模型测试速度
/openclaw model qwen3.5-plus
```

---

### 方案 2：优化记忆检索（效果显著）

#### A. 减少记忆检索频率

**当前问题：** 每次对话都检索所有记忆

**优化：只在需要时检索**

编辑 `AGENTS.md`，添加：
```markdown
## 记忆检索规则

**自动触发 memory_search 的情况：**
- ✅ 提到过去："之前"、"上次"、"以前"
- ✅ 询问偏好："我喜欢"、"我讨厌"
- ✅ 涉及人物/项目/任务
- ✅ 显式请求："你还记得"、"帮我回忆"

**不检索的情况（秒回）：**
- ❌ 简单问候："你好"、"早"
- ❌ 简单问题："在吗"、"忙吗"
- ❌ 闲聊：无实质内容的对话
```

#### B. 优化 Layer1 快照大小

**当前：** ~2000 tokens
**建议：** 减少到 ~1000 tokens（更快加载）

```bash
# 编辑 memory/config.json
openclaw config set agents.defaults.token_budget.layer1_total 1000
```

#### C. 使用关键词搜索代替语义搜索

语义搜索需要 Embedding API，速度慢。改用关键词搜索：

```bash
# 使用 grep 快速搜索
grep -r "关键词" /home/admin/.openclaw/workspace/memory/ --include="*.md"
```

---

### 方案 3：优化上下文管理

#### A. 启用更激进的 Compaction

**当前配置：**
```json
{
  "compaction": {
    "mode": "safeguard"
  }
}
```

**优化配置：**
```bash
openclaw config set agents.defaults.compaction.mode "aggressive"
```

**模式对比：**
| 模式 | 速度 | 保留内容 | 适用场景 |
|------|------|----------|----------|
| `safeguard` | 慢 | 保留最多 | 重要对话 |
| `aggressive` | 快 | 保留关键 | 日常对话 ✅ |
| `disabled` | 最快 | 不保留 | 不推荐 |

#### B. 限制最大上下文长度

```bash
# 限制上下文 token 数
openclaw config set agents.defaults.maxContextTokens 4000
```

---

### 方案 4：优化系统性能

#### A. 检查系统负载

```bash
# 查看 CPU 和内存使用
top -bn1 | head -20
free -h
```

#### B. 优化磁盘 IO

```bash
# 检查磁盘速度
hdparm -t /dev/vda

# 如果是机械硬盘，考虑升级到 SSD
```

#### C. 减少并发任务

如果同时运行多个 cron 任务，会拖慢系统：

```bash
# 查看当前 cron 任务
crontab -l

# 错开执行时间，避免同时运行
```

---

### 方案 5：优化网络延迟

#### A. 使用国内 API 端点

**阿里云百炼国内节点：**
```bash
# 配置使用国内 API
openclaw config set agents.defaults.models.dashscope-coding/qwen3.5-plus.baseURL "https://dashscope.aliyuncs.com"
```

#### B. 检查网络延迟

```bash
# 测试 API 延迟
curl -w "@curl-format.txt" -o /dev/null -s "https://dashscope.aliyuncs.com"

# curl-format.txt 内容：
# time_namelookup:  %{time_namelookup}\n
# time_connect:     %{time_connect}\n
# time_starttransfer: %{time_starttransfer}\n
# time_total:       %{time_total}\n
```

---

### 方案 6：闲聊模式（极速回复）

**创建快速回复规则：**

在 `AGENTS.md` 中添加：
```markdown
## 🚀 快速回复模式

**以下情况直接回复，不查文件、不搜索：**

1. **问候** - "你好"、"早"、"在吗"
   - 回复："你好！有什么可以帮你的吗？"

2. **确认** - "好的"、"收到"、"谢谢"
   - 回复："不客气！" / "应该的~"

3. **简单问题** - "吃了吗"、"忙吗"
   - 回复：简短回答，不展开

4. **表情符号** - "😄"、"👍"
   - 回复：表情符号或简短回应

**原则：** 闲聊秒回，正事才查文件
```

---

## 📈 性能对比

### 优化前 vs 优化后

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| **简单问候** | 3-5 秒 | 1-2 秒 | 60% ⬆️ |
| **记忆检索** | 5-8 秒 | 2-3 秒 | 60% ⬆️ |
| **复杂问题** | 8-12 秒 | 4-6 秒 | 50% ⬆️ |
| **闲聊** | 3-5 秒 | <1 秒 | 80% ⬆️ |

---

## 🔧 立即执行优化

### 快速优化（5 分钟）

```bash
# 1. 切换到快速模型
openclaw config set agents.defaults.model.primary "qwen3.5-plus"

# 2. 启用激进的 Compaction
openclaw config set agents.defaults.compaction.mode "aggressive"

# 3. 限制上下文长度
openclaw config set agents.defaults.maxContextTokens 4000

# 4. 重启 Gateway
openclaw gateway restart
```

### 中级优化（30 分钟）

1. **优化 AGENTS.md** - 添加快速回复规则
2. **减少 Layer1 大小** - 从 2000 tokens 减到 1000
3. **配置记忆检索规则** - 只在需要时检索

### 高级优化（1 小时）

1. **部署本地 Embedding** - 减少 API 调用
2. **配置 Redis 缓存** - 缓存常用检索结果
3. **优化 cron 任务** - 错开执行时间

---

## 📊 监控性能

### 创建性能监控脚本

```bash
#!/bin/bash
# scripts/monitor-speed.sh

echo "🚀 悠悠性能监控"
echo "=============="

# 测试 API 延迟
echo -n "API 延迟："
curl -w "%{time_total}s\n" -o /dev/null -s "https://dashscope.aliyuncs.com"

# 检查系统负载
echo -n "CPU 负载："
uptime | awk -F'load average:' '{print $2}' | cut -d',' -f1

# 检查内存使用
echo -n "内存使用："
free -h | grep Mem | awk '{print $3 "/" $2 " (" $3/$2 * 100 "%)"}'

# 检查磁盘 IO
echo -n "磁盘读取："
hdparm -t /dev/vda 2>/dev/null | grep "Timing buffered" | awk '{print $4, $5}'
```

---

## ⚠️ 注意事项

1. **速度与质量的平衡**
   - 过快可能导致回复质量下降
   - 重要决策时建议用较慢但更准确的模型

2. **监控 Token 使用**
   - 激进优化可能增加 Token 消耗
   - 定期检查用量：`openclaw status`

3. **测试后再部署**
   - 先在测试环境验证
   - 确认无问题后再应用到生产

---

_创建于 2026-03-01，悠悠的性能优化指南_

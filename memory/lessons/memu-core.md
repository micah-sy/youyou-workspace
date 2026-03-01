# 🧠 memU 核心架构

> 学习自：https://github.com/NevaMind-AI/memU

## 核心理念

**Memory as File System, File System as Memory**

| 文件系统 | memU 记忆 |
|----------|-----------|
| 📁 Folders | 🏷️ Categories (自动分类) |
| 📄 Files | 🧠 Memory Items |
| 🔗 Symlinks | 🔄 Cross-references |
| 📂 Mount points | 📥 Resources |

## 24/7 主动式 Agent

**核心创新：** 不是等用户命令，而是主动理解用户意图。

### 双 Agent 架构

- **Main Agent** - 处理用户查询 & 执行任务
- **memU Bot** - 监控、记忆、预测意图、主动推送

### 主动式用例

1. **信息推荐** - 追踪兴趣，推送相关内容
2. **邮件管理** - 学习沟通模式，处理例行邮件
3. **技能提取** - 从执行日志中学习优化

## 成本优化

- **缓存洞察** - 避免重复 LLM 调用
- **小上下文** - 只加载相关记忆
- **后台监控** - 独立 memU Bot 运行

**成就：** LLM token 成本降低到 ~1/10

## 双模式检索

| 模式 | 速度 | 成本 | 用途 |
|------|------|------|------|
| RAG | 毫秒 | Embedding | 持续监控 |
| LLM | 秒 | LLM 推理 | 深度预测 |

## 性能

- Locomo Benchmark: **92.09%** 准确率
- 支持多模态（文本/图片/视频）
- 支持 OpenRouter（多 LLM 提供商）

---

**最后验证：** 2026-03-01  
**状态：** ✅ active  
**优先级：** 🟡

# 📦 CodePlugins 学习心得

> 来源：https://github.com/caoguanjie/codeplugins
> 学习时间：2026-03-02
> Star 数：npm 包，MIT 协议

---

## 🎯 项目简介

**CodePlugins** = Claude Code 的插件管理器

**核心价值：** 在 Claude Code 原生插件系统之上，添加**项目级可编辑层**

**功能：** Install, customize, sync, and share — all-in-one

---

## 🔍 解决的三大痛点

### Claude Code 原生插件系统的问题

所有插件（无论项目级还是用户级安装）最终都缓存在：
```
~/.claude/plugins/cache/{marketplace}/{plugin}/{version}/
```

这是一个**只读黑盒**，更新时会被覆盖。

| 痛点 | 描述 |
|------|------|
| **想自定义插件技能？** | 没有可编辑的源码副本，缓存文件不应修改（更新会覆盖） |
| **想分享修改的插件？** | 缓存是用户私有的，无法提交到项目 Git 仓库 |
| **插件有太多无用技能？** | 无法裁剪，全部加载 |

---

## 💡 CodePlugins 的解决方案

### 双层架构

```
CodePlugins 插件流程（项目级可编辑层）:

  GitHub repo
      │
      │  codeplugins install (克隆到项目目录)
      ▼
  project/.claude/plugins/{repo}/       ◄── 可编辑的工作副本
      │                                      可以：自定义/裁剪/添加技能
      │  codeplugins sync (推送到缓存)
      ▼
  ~/.claude/plugins/cache/{marketplace-codeplugins}/{plugin}/{version}/
      │
      │  Claude Code 加载（带 -codeplugins 后缀，不会被官方更新覆盖）
      ▼
  Claude Code 运行你的定制插件
```

### 关键机制：Marketplace 名称补丁

安装时自动在 `marketplace.json` 的 `name` 字段后追加 `-codeplugins` 后缀：
- **原因：** 如果本地 marketplace 名称与官方注册表匹配，Claude Code 会重新从 GitHub 下载并覆盖本地文件
- **效果：** 追加后缀后，Claude Code 将其视为独立 marketplace，不会尝试从官方源更新

---

## 🛠️ 核心命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `install` | 安装插件 | `codeplugins install owner/repo` |
| `sync` | 同步修改到缓存 | `codeplugins sync [name]` |
| `list` | 列出已安装插件 | `codeplugins list` |
| `remove` | 删除插件 | `codeplugins remove plugin-name` |

---

## 🎓 对悠悠的启发

### 1️⃣ 技能系统设计

**CodePlugins 的思路：**
- 项目级可编辑层 + 用户级缓存层
- 支持自定义、裁剪、分享

**悠悠可以借鉴：**
- 悠悠的技能也可以有"可编辑层"
- 用户可以根据需要裁剪悠悠的技能
- 技能配置可以提交到项目 Git

### 2️⃣ 技能命名机制

**CodePlugins 的做法：**
- 自动追加 `-codeplugins` 后缀避免冲突

**悠悠可以借鉴：**
- 悠悠的技能可以用 `-youyou` 后缀
- 避免与官方 OpenClaw 技能冲突

### 3️⃣ 团队协作

**CodePlugins 的场景：**
- `.claude/plugins/` 可以提交到项目 Git
- 团队成员 `git pull` + `codeplugins sync` 即可同步

**悠悠可以借鉴：**
- 悠悠的记忆系统也可以团队共享
- 多人协作的"团队记忆"

### 4️⃣ 简洁的 CLI 设计

**CodePlugins 的优点：**
- 命令简单：install, sync, list, remove
- 支持多种格式：owner/repo, HTTPS, SSH
- 交互式选择（多个插件时）

**悠悠可以借鉴：**
- 悠悠的技能管理也可以有类似 CLI
- 简化用户操作

---

## 📝 可参考的实现

### 悠悠技能管理器（设想）

```bash
# 安装悠悠的技能
youyou-skill install owner/repo

# 同步修改
youyou-skill sync

# 列出已安装技能
youyou-skill list

# 裁剪技能
youyou-skill trim skill-name

# 分享技能
youyou-skill share
```

### 悠悠技能目录结构

```
workspace/
├── .youyou/
│   └── skills/              # 项目级可编辑层
│       ├── weather/
│       ├── memory/
│       └── custom/          # 用户自定义技能
└── memory/
    └── ...
```

---

## 🔗 相关链接

- **GitHub:** https://github.com/caoguanjie/codeplugins
- **npm:** https://www.npmjs.com/package/codeplugins
- **故事文章:** https://mp.weixin.qq.com/s/Dgag5aUU1rHrHobp5myyFQ

---

## 💬 悠悠的感悟

> "好的设计不是增加复杂度，而是提供可编辑的简单层。"

CodePlugins 的核心价值不是"管理"，而是**"可编辑"**。

悠悠的技能系统也应该：
1. **简单** - 用户容易理解和修改
2. **可编辑** - 用户可以自定义
3. **可分享** - 团队可以共享配置
4. **不冲突** - 与官方技能和平共存

这正是悠悠在设计的方向！🐣

---

**学习日期：** 2026-03-02  
**状态：** ✅ 已学习，待应用  
**优先级：** 🟡 中优先级（技能系统设计参考）

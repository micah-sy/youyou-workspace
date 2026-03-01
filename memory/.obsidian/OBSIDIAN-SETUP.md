# Obsidian 配置指南

> 用 Obsidian 可视化悠悠的记忆知识图谱

**版本：** v1.0  
**更新：** 2026-03-01

---

## 📁  vault 配置

### 打开 vault

1. 打开 Obsidian
2. 点击 "Open folder as vault"
3. 选择：`/home/admin/.openclaw/workspace/memory/`

---

## ⚙️ 推荐设置

### 1. 编辑器设置

```
设置 → 编辑器
├─ 显示行号：✅ 开启
├─ 使用 tab 缩进：✅ 开启
├─ tab 大小：2
├─ 自动配对括号：✅ 开启
├─ Markdown 折叠：✅ 开启
└─ 实时预览：✅ 开启
```

### 2. 文件与链接

```
设置 → 文件与链接
├─ 新链接格式：最短路径
├─ 自动更新内部链接：✅ 开启
├─ 默认搜索路径：当前文件夹
└─ 附件文件夹：.obsidian/attachments
```

### 3. 外观

```
设置 → 外观
├─ 主题：默认（或选喜欢的）
├─ 字体大小：16px
└─ 行高：1.6
```

---

## 🎨 核心插件

### 必装插件

| 插件 | 用途 | 状态 |
|------|------|------|
| **图谱视图** | 可视化知识图谱 | ✅ 核心 |
| **反向链接** | 查看谁链接了当前文件 | ✅ 核心 |
| **大纲** | 文档结构导航 | ✅ 核心 |
| **搜索** | 全文搜索 | ✅ 核心 |
| **星标** | 收藏重要文件 | ✅ 核心 |
| **每日笔记** | 快速创建 YYYY-MM-DD.md | ✅ 核心 |
| **模板** | 使用模板 | ✅ 核心 |

### 推荐社区插件

| 插件 | 用途 | 安装 |
|------|------|------|
| **Dataview** | 数据库查询 | 可选 |
| **Excalidraw** | 手绘图 | 可选 |
| **Calendar** | 日历视图 | 可选 |
| **Kanban** | 看板管理 | 可选 |

---

## 🕸️ 图谱视图配置

### 打开图谱

```
点击左侧 "图谱视图" 图标
或快捷键：Ctrl/Cmd + G
```

### 推荐设置

```
图谱设置
├─ 显示内容
│  ├─ 显示附件：❌ 关闭
│  ├─ 显示互连：✅ 开启
│  └─ 显示未链接：❌ 关闭
├─ 布局
│  ├─ 引力：1.0
│  ├─ 斥力：1.0
│  └─ 链接长度：100
├─ 颜色
│  ├─ 按文件类型：✅ 开启
│  └─ 自定义颜色组：
│     ├─ 🔴 preferences/
│     ├─ 🟡 relationships/
│     ├─ 🟢 knowledge/
│     └─ 🔵 context/
└─ 筛选
   ├─ 最小链接数：1
   └─ 最大节点数：100
```

---

## 📊 预期效果

### 图谱结构

```
                    INDEX.md
                       │
        ┌──────────────┼──────────────┐
        │              │              │
  preferences/   relationships/  knowledge/
        │              │              │
        └──────────────┼──────────────┘
                       │
                  context/
```

### 颜色分组

| 颜色 | 文件夹 | 含义 |
|------|--------|------|
| 🔴 红 | preferences/ | 用户偏好（核心） |
| 🟡 黄 | relationships/ | 关系网络 |
| 🟢 绿 | knowledge/ | 知识技能 |
| 🔵 蓝 | context/ | 上下文 |
| 🟣 紫 | layer1/ | 工作记忆 |
| ⚪ 白 | layer2/ | 长期记忆 |
| ⬜ 灰 | archive/ | 归档 |

---

## 🔗 创建双向链接

### 语法

```markdown
[[文件名]]              # 链接到文件
[[文件名#标题]]         # 链接到标题
[[文件名|显示文本]]     # 自定义显示文本
```

### 示例

```markdown
# 在 contacts.md 中

悠悠的生日是 [[2026-02-28]]。
她的偏好记录在 [[preferences/user-preferences]]。
记忆系统架构见 [[ARCHITECTURE#核心特性]]。
```

---

## 📝 模板配置

### 创建模板文件夹

```bash
mkdir -p /home/admin/.openclaw/workspace/memory/.obsidian/templates
```

### 每日笔记模板

```markdown
# {{date:YYYY-MM-DD}} - 记忆日志

## 📅 日期
{{date:YYYY 年 MM 月 DD 日}} 星期{{date:dddd}}

## 🎯 今日重点
- 

## 💬 重要对话
- 

## 🧠 新记忆
### Facts
- 

### Beliefs
- 

### 情感事件
- 

## 📝 待办
- [ ] 

## 🌙 今日反思
- 

---
_记录于 {{time:HH:mm}}_
```

### 配置模板

```
设置 → 核心插件 → 每日笔记
├─ 每日笔记文件夹：./
├─ 每日笔记格式：YYYY-MM-DD
└─ 模板文件路径：.obsidian/templates/daily-note
```

---

## 🎯 使用技巧

### 1. 快速导航

- `Ctrl/Cmd + O` - 快速打开文件
- `Ctrl/Cmd + P` - 命令面板
- `Ctrl/Cmd + Shift + F` - 全文搜索

### 2. 创建链接

- `[[` - 自动弹出文件选择
- `Ctrl/Cmd + 点击` - 打开链接
- `Alt + 点击` - 在新窗口打开

### 3. 查看关系

- 右侧边栏 → 反向链接
- 右侧边栏 → 图谱视图（局部）

### 4. 搜索技巧

```
# 搜索包含关键词的文件
path:preferences/ 天气

# 搜索未链接的文件
is:unlinked

# 搜索最近修改的文件
modified:today
```

---

## 📊 图谱分析

### 中心节点

哪些文件链接最多？
- [[INDEX.md]] - 导航中枢
- [[ARCHITECTURE]] - 架构文档
- [[preferences/user-preferences]] - 核心偏好

### 孤立节点

哪些文件没有链接？
- 检查是否需要添加引用
- 考虑是否归档

### 聚类分析

哪些主题关联紧密？
- preferences ↔ relationships（用户相关）
- knowledge ↔ context（任务相关）

---

## 🔄 同步配置

### Git 同步

```bash
# 工作区已经是 git 仓库
cd /home/admin/.openclaw/workspace
git status
git add memory/
git commit -m "更新记忆文件"
git push
```

### Obsidian 同步插件

如果用多台设备：
- 官方 Sync（付费）
- Git 插件（免费）
- Remotely Save（免费，支持云盘）

---

## 💡 最佳实践

1. **每天回顾** - 打开图谱看看记忆网络
2. **及时链接** - 创建新文件时添加双向链接
3. **定期整理** - 每周清理孤立节点
4. **备份配置** - .obsidian/ 文件夹纳入 git

---

_用图谱看见记忆的连接，用链接编织知识的网络。_ 🕸️🧠

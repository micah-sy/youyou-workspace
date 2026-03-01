# 🗑️ 扩展清理记录

## 清理日期
2026-03-01 22:07

## 删除的扩展

### 1. DingTalk (钉钉)
- **大小：** ~1.4 GB
- **原因：** 已配置但未启用
- **状态：** ❌ 已删除（未备份）

### 2. WeCom (企业微信)
- **大小：** ~1.8 MB
- **原因：** 已配置但未启用
- **状态：** ❌ 已删除（未备份）

## 当前保留的扩展

| 扩展 | 大小 | 用途 |
|------|------|------|
| **qqbot/** | ~50 MB | ✅ QQ Bot（已启用） |
| **dashscope-cfg/** | ~100 KB | ✅ 阿里云模型配置 |

## 恢复方法

如果需要重新安装：

### DingTalk
```bash
# 从 npm 重新安装
cd /home/admin/.openclaw
npm install @openclaw-china/dingtalk --save
```

### WeCom
```bash
# 从 npm 重新安装
cd /home/admin/.openclaw
npm install @openclaw-china/wecom --save
```

## 清理效果

- **清理前：** 17 GB / 40 GB (46%)
- **清理后：** 15.6 GB / 40 GB (39%)
- **释放空间：** ~1.4 GB ✅

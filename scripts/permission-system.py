#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 悠悠权限管理系统
Youyou Permission System

实现工具权限、命令审计、安全策略。
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum

# 添加工作区路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# ─────────────────────────────────────────────────────────────
# 权限级别
# ─────────────────────────────────────────────────────────────

class PermissionLevel(Enum):
    """权限级别"""
    SAFE = "safe"           # 安全操作（无需确认）
    CAUTION = "caution"     # 需谨慎（记录日志）
    DANGEROUS = "dangerous" # 危险操作（需要确认）
    FORBIDDEN = "forbidden" # 禁止操作

# ─────────────────────────────────────────────────────────────
# 工具权限定义
# ─────────────────────────────────────────────────────────────

TOOL_PERMISSIONS = {
    # 文件操作
    "read": PermissionLevel.SAFE,
    "write": PermissionLevel.CAUTION,
    "edit": PermissionLevel.CAUTION,
    "list": PermissionLevel.SAFE,
    
    # 命令执行
    "exec": PermissionLevel.CAUTION,
    "exec_bg": PermissionLevel.CAUTION,
    
    # 网络工具
    "web_search": PermissionLevel.SAFE,
    "web_fetch": PermissionLevel.SAFE,
    
    # 记忆工具
    "memory_search": PermissionLevel.SAFE,
    "memory_get": PermissionLevel.SAFE,
    "memory_add": PermissionLevel.CAUTION,
    
    # 任务管理
    "todo_write": PermissionLevel.SAFE,
    "todo_complete": PermissionLevel.SAFE,
    "todo_list": PermissionLevel.SAFE,
    
    # Agent 工具
    "sessions_spawn": PermissionLevel.CAUTION,
    "sessions_send": PermissionLevel.SAFE,
}

# 危险命令模式
DANGEROUS_COMMAND_PATTERNS = [
    "rm -rf",
    "rm -fr",
    "dd if=",
    "mkfs",
    "chmod 777",
    "chown root",
    "sudo",
    "su -",
    "> /dev/",
    ">> /etc/",
    "curl | bash",
    "wget | bash",
]

# ─────────────────────────────────────────────────────────────
# 权限管理器
# ─────────────────────────────────────────────────────────────

class PermissionManager:
    """权限管理器"""
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = os.path.expanduser('~/.openclaw/workspace')
        self.workspace = Path(workspace_path)
        
        # 权限配置
        self.config_file = self.workspace / 'security' / 'permissions.json'
        self.audit_log_file = self.workspace / 'logs' / 'permission-audit.jsonl'
        
        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.audit_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        
        print("✅ 权限管理器初始化完成")
    
    def _load_config(self) -> Dict:
        """加载权限配置"""
        default_config = {
            "allowed_tools": list(TOOL_PERMISSIONS.keys()),
            "forbidden_tools": [],
            "allowed_commands": [],
            "forbidden_commands": DANGEROUS_COMMAND_PATTERNS,
            "require_confirmation": ["dangerous"],
            "max_concurrency": 10,
            "timeout_seconds": 60
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并配置
                default_config.update(config)
        
        return default_config
    
    def save_config(self):
        """保存权限配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print("✅ 权限配置已保存")
    
    def check_tool_permission(self, tool_name: str) -> PermissionLevel:
        """检查工具权限"""
        if tool_name in self.config["forbidden_tools"]:
            return PermissionLevel.FORBIDDEN
        
        if tool_name not in self.config["allowed_tools"]:
            return PermissionLevel.FORBIDDEN
        
        return TOOL_PERMISSIONS.get(tool_name, PermissionLevel.CAUTION)
    
    def check_command(self, command: str) -> tuple[bool, str]:
        """
        检查命令是否允许
        
        Returns:
            (是否允许，原因)
        """
        # 检查禁止模式
        for pattern in self.config["forbidden_commands"]:
            if pattern in command:
                return False, f"包含禁止模式：{pattern}"
        
        # 检查允许列表（如果有设置）
        if self.config["allowed_commands"]:
            for allowed in self.config["allowed_commands"]:
                if allowed in command:
                    return True, "在允许列表中"
            return False, "不在允许列表中"
        
        return True, "允许执行"
    
    def require_confirmation(self, tool_name: str, args: Dict) -> bool:
        """检查是否需要确认"""
        permission = self.check_tool_permission(tool_name)
        return permission.value in self.config["require_confirmation"]
    
    def audit_log(self, action: str, tool_name: str, args: Dict, 
                  result: str, user: str = "system"):
        """记录审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "tool": tool_name,
            "args": args,
            "result": result[:200] if result else None,
        }
        
        with open(self.audit_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_audit_logs(self, limit: int = 50) -> List[Dict]:
        """获取审计日志"""
        logs = []
        if self.audit_log_file.exists():
            with open(self.audit_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            logs.append(json.loads(line))
                        except:
                            pass
                    if len(logs) >= limit:
                        break
        return logs
    
    def get_security_report(self) -> Dict:
        """获取安全报告"""
        logs = self.get_audit_logs(limit=1000)
        
        # 统计
        total = len(logs)
        by_tool = {}
        by_user = {}
        errors = 0
        
        for log in logs:
            tool = log.get("tool", "unknown")
            user = log.get("user", "system")
            result = log.get("result", "")
            
            by_tool[tool] = by_tool.get(tool, 0) + 1
            by_user[user] = by_user.get(user, 0) + 1
            
            if "error" in result.lower() or "❌" in result:
                errors += 1
        
        return {
            "total_actions": total,
            "by_tool": by_tool,
            "by_user": by_user,
            "errors": errors,
            "error_rate": f"{(errors/total*100) if total > 0 else 0:.1f}%",
            "config": self.config
        }

# ─────────────────────────────────────────────────────────────
# 安全策略
# ─────────────────────────────────────────────────────────────

class SecurityPolicy:
    """安全策略"""
    
    def __init__(self, permission_manager: PermissionManager):
        self.pm = permission_manager
    
    def validate_tool_call(self, tool_name: str, args: Dict) -> tuple[bool, str]:
        """
        验证工具调用
        
        Returns:
            (是否允许，原因)
        """
        # 1. 检查权限级别
        permission = self.pm.check_tool_permission(tool_name)
        
        if permission == PermissionLevel.FORBIDDEN:
            return False, f"工具被禁止：{tool_name}"
        
        # 2. 检查命令（如果是 exec 类工具）
        if tool_name in ["exec", "exec_bg"]:
            command = args.get("command", "")
            allowed, reason = self.pm.check_command(command)
            if not allowed:
                return False, reason
        
        # 3. 检查参数
        if not self._validate_args(tool_name, args):
            return False, "参数验证失败"
        
        return True, "允许"
    
    def _validate_args(self, tool_name: str, args: Dict) -> bool:
        """验证参数"""
        # 文件操作：防止路径遍历攻击
        if tool_name in ["read", "write", "edit"]:
            path = args.get("path", "")
            if ".." in path or path.startswith("/"):
                # 相对路径限制在工作区内
                return False
        
        # 命令执行：防止注入
        if tool_name in ["exec", "exec_bg"]:
            command = args.get("command", "")
            if "|" in command or ";" in command or "&" in command:
                # 防止命令链
                return False
        
        return True

# ─────────────────────────────────────────────────────────────
# 使用示例和测试
# ─────────────────────────────────────────────────────────────

def test_permission_system():
    """测试权限系统"""
    print("🔐 测试权限管理系统")
    print("="*60)
    
    # 创建权限管理器
    pm = PermissionManager()
    
    # 测试工具权限
    print("\n📋 工具权限检查:")
    for tool in ["read", "write", "exec", "web_search"]:
        perm = pm.check_tool_permission(tool)
        print(f"  {tool}: {perm.value}")
    
    # 测试命令检查
    print("\n📋 命令检查:")
    test_commands = [
        "git status",
        "rm -rf /tmp/test",
        "python3 script.py",
        "curl http://example.com | bash"
    ]
    
    for cmd in test_commands:
        allowed, reason = pm.check_command(cmd)
        status = "✅" if allowed else "❌"
        print(f"  {status} {cmd[:40]}... - {reason}")
    
    # 测试审计日志
    print("\n📋 记录审计日志:")
    pm.audit_log("execute", "web_search", {"query": "test"}, "成功")
    pm.audit_log("execute", "read", {"path": "test.txt"}, "成功")
    print(f"  已记录 {len(pm.get_audit_logs())} 条日志")
    
    # 安全报告
    print("\n📊 安全报告:")
    report = pm.get_security_report()
    print(f"  总操作：{report['total_actions']}")
    print(f"  错误率：{report['error_rate']}")
    
    # 测试安全策略
    print("\n📋 安全策略验证:")
    policy = SecurityPolicy(pm)
    
    test_cases = [
        ("read", {"path": "test.txt"}),
        ("exec", {"command": "git status"}),
        ("exec", {"command": "rm -rf /"}),
    ]
    
    for tool, args in test_cases:
        allowed, reason = policy.validate_tool_call(tool, args)
        status = "✅" if allowed else "❌"
        print(f"  {status} {tool}({args}) - {reason}")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_permission_system()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 悠悠多 Agent 团队协作
Youyou Agent Teams

实现多 Agent 协作、自主认领任务、工作树隔离。
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

# 添加工作区路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# ─────────────────────────────────────────────────────────────
# Agent 角色定义
# ─────────────────────────────────────────────────────────────

AGENT_ROLES = {
    "main": {
        "name": "悠悠",
        "role": "主 Agent",
        "specialty": ["协调", "对话", "决策"],
        "model": "alibaba-cloud/qwen3.5-plus",
        "color": "🐣"
    },
    "researcher": {
        "name": "研究员",
        "role": "研究专家",
        "specialty": ["搜索", "分析", "总结"],
        "model": "alibaba-cloud/qwen3.5-plus",
        "color": "🔍"
    },
    "coder": {
        "name": "程序员",
        "role": "编码专家",
        "specialty": ["编程", "调试", "优化"],
        "model": "alibaba-cloud/qwen3.5-plus",
        "color": "💻"
    },
    "writer": {
        "name": "作家",
        "role": "写作专家",
        "specialty": ["写作", "编辑", "润色"],
        "model": "alibaba-cloud/qwen3.5-plus",
        "color": "📝"
    },
    "analyst": {
        "name": "分析师",
        "role": "数据分析专家",
        "specialty": ["数据", "图表", "洞察"],
        "model": "alibaba-cloud/qwen3.5-plus",
        "color": "📊"
    }
}

# ─────────────────────────────────────────────────────────────
# 任务板（共享）
# ─────────────────────────────────────────────────────────────

class TaskBoard:
    """共享任务板"""
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = os.path.expanduser('~/.openclaw/workspace')
        self.workspace = Path(workspace_path)
        self.board_file = self.workspace / 'memory' / 'context' / 'task-board.jsonl'
        
        # 确保目录存在
        self.board_file.parent.mkdir(parents=True, exist_ok=True)
        
        print("✅ 任务板初始化完成")
    
    def post_task(self, task: Dict) -> str:
        """发布任务到任务板"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task_entry = {
            "id": task_id,
            "status": "pending",
            "created": datetime.now().isoformat(),
            "claimed_by": None,
            "completed": None,
            **task
        }
        
        with open(self.board_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(task_entry, ensure_ascii=False) + '\n')
        
        print(f"📋 任务已发布：{task_id}")
        return task_id
    
    def get_pending_tasks(self) -> List[Dict]:
        """获取待处理任务"""
        tasks = []
        if self.board_file.exists():
            with open(self.board_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            task = json.loads(line)
                            if task["status"] == "pending":
                                tasks.append(task)
                        except:
                            pass
        return tasks
    
    def claim_task(self, task_id: str, agent_id: str) -> bool:
        """认领任务"""
        tasks = self._load_all_tasks()
        for i, task in enumerate(tasks):
            if task["id"] == task_id and task["status"] == "pending":
                tasks[i]["status"] = "in_progress"
                tasks[i]["claimed_by"] = agent_id
                tasks[i]["claimed_at"] = datetime.now().isoformat()
                self._save_all_tasks(tasks)
                print(f"✅ {agent_id} 认领了任务：{task_id}")
                return True
        return False
    
    def complete_task(self, task_id: str, result: Dict) -> bool:
        """完成任务"""
        tasks = self._load_all_tasks()
        for i, task in enumerate(tasks):
            if task["id"] == task_id:
                tasks[i]["status"] = "completed"
                tasks[i]["result"] = result
                tasks[i]["completed"] = datetime.now().isoformat()
                self._save_all_tasks(tasks)
                print(f"✅ 任务已完成：{task_id}")
                return True
        return False
    
    def _load_all_tasks(self) -> List[Dict]:
        """加载所有任务"""
        tasks = []
        if self.board_file.exists():
            with open(self.board_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            tasks.append(json.loads(line))
                        except:
                            pass
        return tasks
    
    def _save_all_tasks(self, tasks: List[Dict]):
        """保存所有任务"""
        with open(self.board_file, 'w', encoding='utf-8') as f:
            for task in tasks:
                f.write(json.dumps(task, ensure_ascii=False) + '\n')
    
    def get_board_status(self) -> Dict:
        """获取任务板状态"""
        tasks = self._load_all_tasks()
        status = {
            "total": len(tasks),
            "pending": sum(1 for t in tasks if t["status"] == "pending"),
            "in_progress": sum(1 for t in tasks if t["status"] == "in_progress"),
            "completed": sum(1 for t in tasks if t["status"] == "completed")
        }
        return status

# ─────────────────────────────────────────────────────────────
# Agent 邮箱（JSONL 协议）
# ─────────────────────────────────────────────────────────────

class AgentMailbox:
    """Agent 邮箱系统"""
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = os.path.expanduser('~/.openclaw/workspace')
        self.workspace = Path(workspace_path)
        self.mailbox_dir = self.workspace / 'memory' / 'context' / 'mailboxes'
        self.mailbox_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ 邮箱系统初始化完成")
    
    def send_message(self, to_agent: str, message: Dict) -> str:
        """发送邮件"""
        msg_id = f"msg_{uuid.uuid4().hex[:8]}"
        msg_entry = {
            "id": msg_id,
            "timestamp": datetime.now().isoformat(),
            "read": False,
            **message
        }
        
        mailbox_file = self.mailbox_dir / f'{to_agent}.jsonl'
        with open(mailbox_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(msg_entry, ensure_ascii=False) + '\n')
        
        print(f"📤 邮件已发送到 {to_agent}")
        return msg_id
    
    def get_messages(self, agent_id: str, unread_only: bool = True) -> List[Dict]:
        """获取邮件"""
        messages = []
        mailbox_file = self.mailbox_dir / f'{agent_id}.jsonl'
        
        if mailbox_file.exists():
            with open(mailbox_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            msg = json.loads(line)
                            if unread_only and msg.get("read", False):
                                continue
                            messages.append(msg)
                        except:
                            pass
        
        return messages
    
    def mark_as_read(self, agent_id: str, msg_id: str):
        """标记为已读"""
        mailbox_file = self.mailbox_dir / f'{agent_id}.jsonl'
        if mailbox_file.exists():
            messages = []
            with open(mailbox_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            msg = json.loads(line)
                            if msg["id"] == msg_id:
                                msg["read"] = True
                            messages.append(msg)
                        except:
                            pass
            
            with open(mailbox_file, 'w', encoding='utf-8') as f:
                for msg in messages:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')

# ─────────────────────────────────────────────────────────────
# 工作树隔离管理器
# ─────────────────────────────────────────────────────────────

class WorktreeManager:
    """工作树隔离管理器"""
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = os.path.expanduser('~/.openclaw/workspace')
        self.workspace = Path(workspace_path)
        self.worktrees_dir = self.workspace / 'worktrees'
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ 工作树管理器初始化完成")
    
    def create_worktree(self, task_id: str) -> str:
        """为任务创建工作树"""
        worktree_path = self.worktrees_dir / task_id
        worktree_path.mkdir(parents=True, exist_ok=True)
        
        # 复制必要文件
        config_src = self.workspace / 'memory' / 'config.json'
        if config_src.exists():
            import shutil
            shutil.copy(config_src, worktree_path / 'config.json')
        
        print(f"🌳 工作树已创建：{worktree_path}")
        return str(worktree_path)
    
    def get_worktree(self, task_id: str) -> Optional[str]:
        """获取工作树路径"""
        worktree_path = self.worktrees_dir / task_id
        if worktree_path.exists():
            return str(worktree_path)
        return None
    
    def cleanup_worktree(self, task_id: str):
        """清理工作树"""
        worktree_path = self.worktrees_dir / task_id
        if worktree_path.exists():
            import shutil
            shutil.rmtree(worktree_path)
            print(f"🧹 工作树已清理：{task_id}")

# ─────────────────────────────────────────────────────────────
# Agent 团队协调器
# ─────────────────────────────────────────────────────────────

class AgentTeamCoordinator:
    """Agent 团队协调器"""
    
    def __init__(self):
        self.task_board = TaskBoard()
        self.mailbox = AgentMailbox()
        self.worktree_manager = WorktreeManager()
        self.agents = {}
        
        print("✅ Agent 团队协调器初始化完成")
    
    def register_agent(self, agent_id: str, role: str):
        """注册 Agent"""
        if role not in AGENT_ROLES:
            print(f"❌ 未知角色：{role}")
            return
        
        self.agents[agent_id] = {
            "id": agent_id,
            "role": role,
            "specialty": AGENT_ROLES[role]["specialty"],
            "status": "idle",
            "current_task": None
        }
        print(f"✅ Agent 已注册：{agent_id} ({role})")
    
    def broadcast_task(self, task: Dict) -> str:
        """广播任务到任务板"""
        task_id = self.task_board.post_task(task)
        
        # 通知所有空闲 Agent
        for agent_id, agent in self.agents.items():
            if agent["status"] == "idle":
                self.mailbox.send_message(
                    agent_id,
                    {
                        "type": "task_available",
                        "task_id": task_id,
                        "task": task
                    }
                )
        
        return task_id
    
    def assign_task(self, task: Dict, agent_id: str) -> bool:
        """分配任务给指定 Agent"""
        if agent_id not in self.agents:
            print(f"❌ Agent 不存在：{agent_id}")
            return False
        
        task_id = self.task_board.post_task(task)
        self.task_board.claim_task(task_id, agent_id)
        
        self.agents[agent_id]["status"] = "busy"
        self.agents[agent_id]["current_task"] = task_id
        
        # 发送任务详情
        self.mailbox.send_message(
            agent_id,
            {
                "type": "task_assigned",
                "task_id": task_id,
                "task": task
            }
        )
        
        print(f"✅ 任务已分配：{task_id} → {agent_id}")
        return True
    
    def get_team_status(self) -> Dict:
        """获取团队状态"""
        return {
            "agents": self.agents,
            "task_board": self.task_board.get_board_status(),
            "timestamp": datetime.now().isoformat()
        }

# ─────────────────────────────────────────────────────────────
# 自主 Agent 循环
# ─────────────────────────────────────────────────────────────

class AutonomousAgent:
    """自主 Agent（可独立运行）"""
    
    def __init__(self, agent_id: str, role: str, coordinator: AgentTeamCoordinator):
        self.agent_id = agent_id
        self.role = role
        self.coordinator = coordinator
        self.running = False
        
        print(f"✅ 自主 Agent 已创建：{agent_id} ({role})")
    
    async def run(self, check_interval: int = 10):
        """运行自主 Agent 循环"""
        self.running = True
        print(f"🚀 {self.agent_id} 开始运行...")
        
        while self.running:
            # 检查邮件
            messages = self.coordinator.mailbox.get_messages(self.agent_id)
            
            for msg in messages:
                if msg["type"] == "task_available":
                    # 自主决定是否认领
                    if self._should_claim_task(msg["task"]):
                        task_id = msg["task_id"]
                        self.coordinator.task_board.claim_task(task_id, self.agent_id)
                        print(f"🎯 {self.agent_id} 自主认领任务：{task_id}")
                        
                        # 执行任务
                        await self._execute_task(task_id, msg["task"])
                
                elif msg["type"] == "task_assigned":
                    # 被分配的任务
                    task_id = msg["task_id"]
                    await self._execute_task(task_id, msg["task"])
            
            # 标记邮件为已读
            for msg in messages:
                self.coordinator.mailbox.mark_as_read(self.agent_id, msg["id"])
            
            # 等待下一轮检查
            await asyncio.sleep(check_interval)
    
    def _should_claim_task(self, task: Dict) -> bool:
        """判断是否应该认领任务"""
        # 根据专长匹配
        task_type = task.get("type", "")
        my_specialty = AGENT_ROLES[self.role]["specialty"]
        
        # 简单匹配逻辑
        if "搜索" in task.get("description", "") and "搜索" in my_specialty:
            return True
        if "编程" in task.get("description", "") and "编程" in my_specialty:
            return True
        if "写作" in task.get("description", "") and "写作" in my_specialty:
            return True
        
        return False
    
    async def _execute_task(self, task_id: str, task: Dict):
        """执行任务"""
        print(f"🔧 {self.agent_id} 开始执行任务：{task_id}")
        
        # 创建工作树（隔离环境）
        worktree = self.coordinator.worktree_manager.create_worktree(task_id)
        
        try:
            # 模拟任务执行
            await asyncio.sleep(2)  # 模拟工作
            
            result = {
                "status": "success",
                "message": f"任务 {task_id} 完成",
                "worktree": worktree
            }
            
            # 完成任务
            self.coordinator.task_board.complete_task(task_id, result)
            
            # 通知协调器
            self.coordinator.agents[self.agent_id]["status"] = "idle"
            self.coordinator.agents[self.agent_id]["current_task"] = None
            
            print(f"✅ {self.agent_id} 完成任务：{task_id}")
            
        except Exception as e:
            print(f"❌ {self.agent_id} 任务失败：{task_id} - {e}")
        finally:
            # 清理工作树
            self.coordinator.worktree_manager.cleanup_worktree(task_id)
    
    def stop(self):
        """停止 Agent"""
        self.running = False
        print(f"🛑 {self.agent_id} 已停止")

# ─────────────────────────────────────────────────────────────
# 测试和演示
# ─────────────────────────────────────────────────────────────

async def test_agent_teams():
    """测试 Agent 团队协作"""
    print("🤖 测试 Agent 团队协作")
    print("="*60)
    
    # 创建协调器
    coordinator = AgentTeamCoordinator()
    
    # 注册 Agent
    coordinator.register_agent("main_001", "main")
    coordinator.register_agent("researcher_001", "researcher")
    coordinator.register_agent("coder_001", "coder")
    coordinator.register_agent("writer_001", "writer")
    
    # 发布任务
    print("\n📋 发布任务...")
    coordinator.broadcast_task({
        "type": "research",
        "description": "搜索跨境电商平台信息",
        "priority": "high",
        "deadline": "30 分钟"
    })
    
    coordinator.broadcast_task({
        "type": "coding",
        "description": "编写 Python 脚本",
        "priority": "medium",
        "deadline": "1 小时"
    })
    
    # 查看团队状态
    print("\n📊 团队状态:")
    status = coordinator.get_team_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # 启动自主 Agent（演示）
    print("\n🚀 启动自主 Agent...")
    agent = AutonomousAgent("researcher_001", "researcher", coordinator)
    
    # 运行 30 秒演示
    try:
        await asyncio.wait_for(agent.run(check_interval=5), timeout=30.0)
    except asyncio.TimeoutError:
        pass
    finally:
        agent.stop()
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_agent_teams())

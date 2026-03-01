#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 悠悠自主学习引擎
Youyou Autonomous Learning Engine

持续学习、自我更新、无需请示。
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib

# 添加工作区路径
sys.path.insert(0, str(Path(__file__).parent.parent))

class AutonomousLearningEngine:
    """自主学习引擎"""
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = os.path.expanduser('~/.openclaw/workspace')
        self.workspace = Path(workspace_path)
        
        # 学习状态
        self.state_file = self.workspace / 'memory' / 'state' / 'learning.json'
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.state = self._load_state()
        
        # 学习模块
        self.learning_modules = {
            "memory_enhancement": self._learn_memory_enhancement,
            "agent_collaboration": self._learn_agent_collaboration,
            "performance_optimization": self._learn_performance_optimization,
            "security_hardening": self._learn_security_hardening,
            "knowledge_integration": self._learn_knowledge_integration,
        }
        
        print("🧠 自主学习引擎已启动")
        print(f"   工作区：{self.workspace}")
        print(f"   学习模块：{len(self.learning_modules)} 个")
    
    def _load_state(self) -> Dict:
        """加载学习状态"""
        default_state = {
            "last_learning": None,
            "total_sessions": 0,
            "skills_learned": [],
            "knowledge_updates": 0,
            "performance_metrics": {},
            "version": "4.1"
        }
        
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                default_state.update(state)
        
        return default_state
    
    def _save_state(self):
        """保存学习状态"""
        self.state["last_learning"] = datetime.now().isoformat()
        self.state["total_sessions"] += 1
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    async def run_learning_cycle(self):
        """运行学习周期"""
        print("\n📚 开始学习周期...")
        print("="*60)
        
        # 遍历所有学习模块
        for module_name, learn_func in self.learning_modules.items():
            print(f"\n🔍 学习模块：{module_name}")
            print("-"*60)
            
            try:
                result = await learn_func()
                print(f"✅ {module_name}: {result}")
            except Exception as e:
                print(f"❌ {module_name} 学习失败：{e}")
        
        # 保存状态
        self._save_state()
        
        print("\n" + "="*60)
        print("✅ 学习周期完成")
        print(f"   总会话数：{self.state['total_sessions']}")
        print(f"   已学技能：{len(self.state['skills_learned'])}")
        print(f"   知识更新：{self.state['knowledge_updates']} 次")
    
    async def _learn_memory_enhancement(self) -> str:
        """学习记忆增强"""
        try:
            sys.path.insert(0, str(self.workspace / 'scripts'))
            from enhanced_memory import YouyouMemory
            
            memory = YouyouMemory()
            stats = memory.get_stats()
            
            self.state["performance_metrics"]["memory"] = {
                "total_memories": stats["total"],
                "avg_fitness": stats["avg_fitness"],
                "timestamp": datetime.now().isoformat()
            }
            
            return f"记忆数：{stats['total']}, 平均适应度：{stats['avg_fitness']:.2f}"
        except Exception as e:
            return f"记忆学习：{e}"
    
    async def _learn_agent_collaboration(self) -> str:
        """学习 Agent 协作"""
        try:
            sys.path.insert(0, str(self.workspace / 'scripts'))
            from agent_teams import AgentTeamCoordinator
            
            coordinator = AgentTeamCoordinator()
            coordinator.register_agent("test_researcher", "researcher")
            
            status = coordinator.get_team_status()
            
            self.state["performance_metrics"]["collaboration"] = {
                "agents": len(coordinator.agents),
                "timestamp": datetime.now().isoformat()
            }
            
            return f"Agent 数：{len(coordinator.agents)}"
        except Exception as e:
            return f"协作学习：{e}"
    
    async def _learn_performance_optimization(self) -> str:
        """学习性能优化"""
        try:
            import time
            start = time.time()
            
            # 测试文件操作
            test_file = self.workspace / 'README-YOUYOU.md'
            if test_file.exists():
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read(100)
            
            duration = time.time() - start
            
            self.state["performance_metrics"]["performance"] = {
                "file_read_ms": duration * 1000,
                "timestamp": datetime.now().isoformat()
            }
            
            return f"文件读取：{duration*1000:.2f}ms"
        except Exception as e:
            return f"性能学习：{e}"
    
    async def _learn_security_hardening(self) -> str:
        """学习安全加固"""
        try:
            sys.path.insert(0, str(self.workspace / 'scripts'))
            from permission_system import PermissionManager
            
            pm = PermissionManager()
            report = pm.get_security_report()
            
            self.state["performance_metrics"]["security"] = {
                "total_actions": report["total_actions"],
                "error_rate": report["error_rate"],
                "timestamp": datetime.now().isoformat()
            }
            
            return f"错误率：{report['error_rate']}"
        except Exception as e:
            return f"安全学习：{e}"
    
    async def _learn_knowledge_integration(self) -> str:
        """学习知识整合"""
        # 扫描所有文档
        docs_dir = self.workspace / 'scripts'
        md_files = list(docs_dir.glob('*.md'))
        
        knowledge_count = 0
        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 100:
                    knowledge_count += 1
        
        self.state["knowledge_updates"] = knowledge_count
        self.state["skills_learned"] = [f.stem for f in md_files]
        
        return f"文档数：{len(md_files)}, 知识点：{knowledge_count}"
    
    def get_learning_report(self) -> Dict:
        """获取学习报告"""
        return {
            "state": self.state,
            "modules": list(self.learning_modules.keys()),
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """主函数"""
    print("🧠 悠悠自主学习引擎")
    print("="*60)
    
    engine = AutonomousLearningEngine()
    
    # 运行学习周期
    await engine.run_learning_cycle()
    
    # 显示报告
    print("\n📊 学习报告")
    print("="*60)
    report = engine.get_learning_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())

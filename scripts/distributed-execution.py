#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 悠悠分布式任务执行
Youyou Distributed Task Execution

支持多节点、任务分发、结果聚合。
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

# ─────────────────────────────────────────────────────────────
# 任务分发器
# ─────────────────────────────────────────────────────────────

class TaskDispatcher:
    """分布式任务分发器"""
    
    def __init__(self):
        self.nodes = {}  # 节点注册
        self.task_queue = asyncio.Queue()
        self.results = {}
        
        print("✅ 任务分发器初始化完成")
    
    def register_node(self, node_id: str, node_info: Dict):
        """注册节点"""
        self.nodes[node_id] = {
            "id": node_id,
            "info": node_info,
            "status": "idle",
            "current_task": None,
            "last_heartbeat": datetime.now().isoformat()
        }
        print(f"✅ 节点已注册：{node_id}")
    
    def unregister_node(self, node_id: str):
        """注销节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            print(f"🗑️ 节点已注销：{node_id}")
    
    async def dispatch_task(self, task: Dict) -> str:
        """分发任务"""
        task_id = self._generate_task_id(task)
        
        # 添加到队列
        await self.task_queue.put({
            "id": task_id,
            "task": task,
            "created": datetime.now().isoformat()
        })
        
        # 通知空闲节点
        await self._notify_idle_nodes(task_id)
        
        print(f"📤 任务已分发：{task_id}")
        return task_id
    
    async def _notify_idle_nodes(self, task_id: str):
        """通知空闲节点"""
        for node_id, node in self.nodes.items():
            if node["status"] == "idle":
                # 这里应该通过某种机制通知节点
                # 简化处理：直接分配
                node["status"] = "busy"
                node["current_task"] = task_id
                print(f"  → 通知节点：{node_id}")
                break
    
    def _generate_task_id(self, task: Dict) -> str:
        """生成任务 ID"""
        content = json.dumps(task, sort_keys=True)
        return f"task_{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    async def get_result(self, task_id: str, timeout: int = 60) -> Optional[Dict]:
        """获取任务结果"""
        start = datetime.now()
        
        while (datetime.now() - start).total_seconds() < timeout:
            if task_id in self.results:
                result = self.results.pop(task_id)
                # 释放节点
                for node in self.nodes.values():
                    if node["current_task"] == task_id:
                        node["status"] = "idle"
                        node["current_task"] = None
                return result
            
            await asyncio.sleep(0.5)
        
        return None
    
    def submit_result(self, task_id: str, result: Dict):
        """提交结果"""
        self.results[task_id] = {
            "task_id": task_id,
            "result": result,
            "completed": datetime.now().isoformat()
        }
        print(f"✅ 结果已提交：{task_id}")
    
    def get_status(self) -> Dict:
        """获取分发器状态"""
        return {
            "nodes": self.nodes,
            "queue_size": self.task_queue.qsize(),
            "pending_results": len(self.results),
            "timestamp": datetime.now().isoformat()
        }

# ─────────────────────────────────────────────────────────────
# 工作节点
# ─────────────────────────────────────────────────────────────

class WorkerNode:
    """工作节点"""
    
    def __init__(self, node_id: str, dispatcher: TaskDispatcher):
        self.node_id = node_id
        self.dispatcher = dispatcher
        self.running = False
        self.tasks_completed = 0
        
        print(f"✅ 工作节点已创建：{node_id}")
    
    async def run(self, check_interval: int = 5):
        """运行工作节点"""
        self.running = True
        
        # 注册到分发器
        self.dispatcher.register_node(self.node_id, {
            "type": "worker",
            "created": datetime.now().isoformat()
        })
        
        print(f"🚀 工作节点 {self.node_id} 开始运行...")
        
        while self.running:
            # 检查是否有任务
            try:
                task_item = self.dispatcher.task_queue.get_nowait()
                task_id = task_item["id"]
                task = task_item["task"]
                
                print(f"📥 节点 {self.node_id} 接收任务：{task_id}")
                
                # 执行任务（模拟）
                result = await self._execute_task(task)
                
                # 提交结果
                self.dispatcher.submit_result(task_id, result)
                self.tasks_completed += 1
                
            except asyncio.QueueEmpty:
                pass
            
            # 发送心跳
            self._send_heartbeat()
            
            await asyncio.sleep(check_interval)
    
    async def _execute_task(self, task: Dict) -> Dict:
        """执行任务"""
        task_type = task.get("type", "unknown")
        
        # 模拟执行
        await asyncio.sleep(1)
        
        return {
            "status": "success",
            "node": self.node_id,
            "task_type": task_type,
            "message": f"任务 {task_type} 完成"
        }
    
    def _send_heartbeat(self):
        """发送心跳"""
        if self.node_id in self.dispatcher.nodes:
            self.dispatcher.nodes[self.node_id]["last_heartbeat"] = datetime.now().isoformat()
    
    def stop(self):
        """停止节点"""
        self.running = False
        self.dispatcher.unregister_node(self.node_id)
        print(f"🛑 工作节点 {self.node_id} 已停止")

# ─────────────────────────────────────────────────────────────
# 分布式协调器
# ─────────────────────────────────────────────────────────────

class DistributedCoordinator:
    """分布式协调器"""
    
    def __init__(self):
        self.dispatcher = TaskDispatcher()
        self.workers = []
        
        print("✅ 分布式协调器初始化完成")
    
    def add_worker(self, node_id: str) -> WorkerNode:
        """添加工作节点"""
        worker = WorkerNode(node_id, self.dispatcher)
        self.workers.append(worker)
        return worker
    
    async def run_cluster(self, num_workers: int = 3, duration: int = 30):
        """运行集群"""
        print(f"🌐 启动分布式集群（{num_workers} 个节点）...")
        
        # 创建工作节点
        for i in range(num_workers):
            self.add_worker(f"worker_{i}")
        
        # 启动所有节点
        tasks = []
        for worker in self.workers:
            tasks.append(asyncio.create_task(worker.run(check_interval=2)))
        
        # 提交一些测试任务
        asyncio.create_task(self._submit_test_tasks())
        
        # 运行指定时间
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=duration
            )
        except asyncio.TimeoutError:
            pass
        finally:
            # 停止所有节点
            for worker in self.workers:
                worker.stop()
        
        print("✅ 集群运行完成")
    
    async def _submit_test_tasks(self):
        """提交测试任务"""
        test_tasks = [
            {"type": "search", "query": "任务 1"},
            {"type": "analyze", "data": "任务 2"},
            {"type": "process", "input": "任务 3"},
            {"type": "search", "query": "任务 4"},
            {"type": "analyze", "data": "任务 5"},
        ]
        
        for task in test_tasks:
            await self.dispatcher.dispatch_task(task)
            await asyncio.sleep(0.5)
    
    def get_cluster_status(self) -> Dict:
        """获取集群状态"""
        return {
            "dispatcher": self.dispatcher.get_status(),
            "workers": len(self.workers),
            "total_completed": sum(w.tasks_completed for w in self.workers),
            "timestamp": datetime.now().isoformat()
        }

# ─────────────────────────────────────────────────────────────
# 测试
# ─────────────────────────────────────────────────────────────

async def test_distributed_execution():
    """测试分布式执行"""
    print("🌐 测试分布式任务执行")
    print("="*60)
    
    # 创建协调器
    coordinator = DistributedCoordinator()
    
    # 运行集群（3 个节点，30 秒）
    await coordinator.run_cluster(num_workers=3, duration=15)
    
    # 显示状态
    print("\n📊 集群状态:")
    status = coordinator.get_cluster_status()
    print(f"  工作节点：{status['workers']} 个")
    print(f"  完成任务：{status['total_completed']} 个")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_distributed_execution())

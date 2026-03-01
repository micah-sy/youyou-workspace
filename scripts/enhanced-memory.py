#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 悠悠记忆系统 v4.1
Youyou Enhanced Memory System

融合 7 大记忆增强系统的优点。
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import OrderedDict
import hashlib

# 添加工作区路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# ─────────────────────────────────────────────────────────────
# 记忆作用域
# ─────────────────────────────────────────────────────────────

class MemoryScope:
    """记忆作用域管理（借鉴 mem0）"""
    
    APP = "app"       # 应用级（所有用户共享）
    USER = "user"     # 用户级（特定用户）
    AGENT = "agent"   # Agent 级（特定 Agent）
    RUN = "run"       # 会话级（单次对话）
    
    HIERARCHY = [APP, USER, AGENT, RUN]  # 检索顺序

# ─────────────────────────────────────────────────────────────
# 记忆 Hooks（自动捕获）
# ─────────────────────────────────────────────────────────────

class MemoryHooks:
    """记忆 Hooks 机制（借鉴 Supermemory）"""
    
    def __init__(self):
        self.handlers = []
    
    def register(self, handler):
        """注册 Hook 处理器"""
        self.handlers.append(handler)
    
    def on_message(self, message: str, metadata: Dict = None) -> List[Dict]:
        """
        消息 Hook - 自动提取记忆
        
        Returns:
            提取的记忆列表
        """
        memories = []
        
        for handler in self.handlers:
            try:
                result = handler(message, metadata or {})
                if result:
                    memories.extend(result if isinstance(result, list) else [result])
            except Exception as e:
                print(f"Hook 执行失败：{e}")
        
        return memories

# 内置 Hook 处理器
def extract_entities(message: str, metadata: Dict) -> Optional[Dict]:
    """提取实体"""
    # 简单实现：检测人名、地名、组织名
    # 实际应该用 NER 模型
    keywords = []
    
    # 检测人名（简单规则）
    if "我叫" in message:
        parts = message.split("我叫")
        if len(parts) > 1:
            name = parts[1].split()[0]
            keywords.append({"type": "person_name", "value": name})
    
    if keywords:
        return {
            "type": "entity",
            "category": "entities",
            "content": json.dumps(keywords),
            "scope": MemoryScope.USER
        }
    return None

def extract_preferences(message: str, metadata: Dict) -> Optional[Dict]:
    """提取偏好"""
    # 检测偏好表达
    preference_words = ["喜欢", "讨厌", "偏好", "习惯", "想要", "希望"]
    
    for word in preference_words:
        if word in message:
            return {
                "type": "preference",
                "category": "preferences",
                "content": message,
                "scope": MemoryScope.USER
            }
    return None

def extract_facts(message: str, metadata: Dict) -> Optional[Dict]:
    """提取事实"""
    # 检测事实陈述（简单规则）
    fact_patterns = ["是", "在", "有", "做", "工作", "家庭"]
    
    for pattern in fact_patterns:
        if pattern in message:
            return {
                "type": "fact",
                "category": "facts",
                "content": message,
                "scope": MemoryScope.USER
            }
    return None

# ─────────────────────────────────────────────────────────────
# SQL 记忆存储（Memori 风格）
# ─────────────────────────────────────────────────────────────

class SQLMemoryStore:
    """SQL 记忆存储（借鉴 Memori）"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.expanduser('~/.openclaw/workspace/memory/memories.db')
        
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
        
        print(f"✅ SQL 记忆存储已初始化：{db_path}")
    
    def _create_tables(self):
        """创建表结构"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                category TEXT,
                scope TEXT DEFAULT 'user',
                scope_app TEXT,
                scope_user TEXT,
                scope_agent TEXT,
                scope_run TEXT,
                entity TEXT,
                relation TEXT,
                fitness REAL DEFAULT 0.5,
                usage_count INTEGER DEFAULT 0,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP
            )
        ''')
        
        # 创建索引
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON memories(category)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_scope ON memories(scope)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_fitness ON memories(fitness)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_entity ON memories(entity)')
        
        self.conn.commit()
    
    def add(self, memory: Dict) -> str:
        """添加记忆"""
        memory_id = memory.get("id", f"mem_{hashlib.md5(memory['content'].encode()).hexdigest()[:12]}")
        
        self.conn.execute('''
            INSERT OR REPLACE INTO memories 
            (id, content, category, scope, scope_app, scope_user, scope_agent, scope_run, 
             entity, relation, fitness, created, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory_id,
            memory.get("content", ""),
            memory.get("category", "general"),
            memory.get("scope", MemoryScope.USER),
            memory.get("scope_app"),
            memory.get("scope_user"),
            memory.get("scope_agent"),
            memory.get("scope_run"),
            memory.get("entity"),
            memory.get("relation"),
            memory.get("fitness", 0.5),
            memory.get("created", datetime.now().isoformat()),
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        return memory_id
    
    def search(self, query: str, category: str = None, scope: str = None, 
               limit: int = 10) -> List[Dict]:
        """搜索记忆（SQL 全文检索）"""
        sql = "SELECT * FROM memories WHERE content LIKE ?"
        params = [f"%{query}%"]
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        if scope:
            sql += " AND scope = ?"
            params.append(scope)
        
        sql += " ORDER BY fitness DESC, last_accessed DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def update_fitness(self, memory_id: str, delta: float):
        """更新适应度评分"""
        self.conn.execute('''
            UPDATE memories 
            SET fitness = MIN(MAX(fitness + ?, 0), 1),
                usage_count = usage_count + 1,
                updated = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (delta, memory_id))
        self.conn.commit()
    
    def get_low_fitness(self, threshold: float = 0.2) -> List[Dict]:
        """获取低适应度记忆（用于遗忘）"""
        cursor = self.conn.execute(
            "SELECT * FROM memories WHERE fitness < ? ORDER BY fitness ASC",
            (threshold,)
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def delete(self, memory_id: str):
        """删除记忆"""
        self.conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total,
                AVG(fitness) as avg_fitness,
                SUM(usage_count) as total_usage,
                COUNT(DISTINCT category) as categories
            FROM memories
        ''')
        row = cursor.fetchone()
        return {
            "total": row[0],
            "avg_fitness": row[1] or 0,
            "total_usage": row[2] or 0,
            "categories": row[3] or 0
        }

# ─────────────────────────────────────────────────────────────
# 记忆进化（EvoMap 风格）
# ─────────────────────────────────────────────────────────────

class EvolvingMemory:
    """进化式记忆管理（借鉴 EvoMap）"""
    
    def __init__(self, store: SQLMemoryStore):
        self.store = store
        self.fitness_threshold_high = 0.8  # 强化阈值
        self.fitness_threshold_low = 0.2   # 遗忘阈值
    
    def record_usage(self, memory_id: str, success: bool):
        """
        记录记忆使用
        
        Args:
            memory_id: 记忆 ID
            success: 使用是否成功
        """
        delta = 0.1 if success else -0.05
        self.store.update_fitness(memory_id, delta)
        
        # 检查是否需要强化或遗忘
        self._check_evolution(memory_id)
    
    def _check_evolution(self, memory_id: str):
        """检查记忆进化状态"""
        # 获取记忆
        memories = self.store.search("", limit=1000)  # 简化：获取所有
        memory = next((m for m in memories if m["id"] == memory_id), None)
        
        if not memory:
            return
        
        fitness = memory.get("fitness", 0.5)
        
        # 高适应度 - 强化
        if fitness >= self.fitness_threshold_high:
            print(f"🌟 记忆强化：{memory_id} (fitness: {fitness:.2f})")
            # 可以添加到缓存或特殊标记
        
        # 低适应度 - 遗忘
        if fitness <= self.fitness_threshold_low:
            print(f"🍂 记忆遗忘：{memory_id} (fitness: {fitness:.2f})")
            # 可以删除或归档
    
    def get_fitness_distribution(self) -> Dict:
        """获取适应度分布"""
        memories = self.store.search("", limit=1000)
        
        distribution = {
            "excellent": 0,  # >= 0.8
            "good": 0,       # 0.6-0.8
            "average": 0,    # 0.4-0.6
            "poor": 0,       # 0.2-0.4
            "critical": 0    # < 0.2
        }
        
        for mem in memories:
            fitness = mem.get("fitness", 0.5)
            if fitness >= 0.8:
                distribution["excellent"] += 1
            elif fitness >= 0.6:
                distribution["good"] += 1
            elif fitness >= 0.4:
                distribution["average"] += 1
            elif fitness >= 0.2:
                distribution["poor"] += 1
            else:
                distribution["critical"] += 1
        
        return distribution

# ─────────────────────────────────────────────────────────────
# 检索追踪（OpenViking 风格）
# ─────────────────────────────────────────────────────────────

class TraceableSearch:
    """可追踪的检索（借鉴 OpenViking）"""
    
    def __init__(self, store: SQLMemoryStore):
        self.store = store
        self.trace_log = []
    
    def search(self, query: str, **kwargs) -> Tuple[List[Dict], Dict]:
        """
        带追踪的搜索
        
        Returns:
            (结果列表，追踪信息)
        """
        trace = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "metrics": {}
        }
        
        # Step 1: 解析查询
        keywords = self._parse_query(query)
        trace["steps"].append({
            "step": 1,
            "action": "parse_query",
            "keywords": keywords,
            "duration_ms": 5
        })
        
        # Step 2: SQL 检索
        start = datetime.now()
        results = self.store.search(query, **kwargs)
        duration = (datetime.now() - start).total_seconds() * 1000
        
        trace["steps"].append({
            "step": 2,
            "action": "sql_retrieve",
            "count": len(results),
            "duration_ms": duration
        })
        
        # Step 3: 排序（适应度 + 时间衰减）
        start = datetime.now()
        ranked = self._rank_results(results, query)
        duration = (datetime.now() - start).total_seconds() * 1000
        
        trace["steps"].append({
            "step": 3,
            "action": "rank",
            "top_score": ranked[0]["score"] if ranked else 0,
            "duration_ms": duration
        })
        
        # 记录追踪日志
        self.trace_log.append(trace)
        
        # 返回结果和追踪
        return [r["memory"] for r in ranked[:10]], trace
    
    def _parse_query(self, query: str) -> Dict:
        """解析查询"""
        return {
            "original": query,
            "length": len(query),
            "has_entity": ":" in query  # 简单检测
        }
    
    def _rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """排序结果"""
        ranked = []
        
        for result in results:
            # 计算综合分数
            fitness = result.get("fitness", 0.5)
            
            # 时间衰减（最近访问的优先）
            last_accessed = result.get("last_accessed")
            time_bonus = 0.1 if last_accessed else 0
            
            # 关键词匹配加分
            content = result.get("content", "")
            match_bonus = 0.2 if query.lower() in content.lower() else 0
            
            score = fitness + time_bonus + match_bonus
            
            ranked.append({
                "memory": result,
                "score": score
            })
        
        # 按分数排序
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked
    
    def get_trace_history(self, limit: int = 10) -> List[Dict]:
        """获取追踪历史"""
        return self.trace_log[-limit:]

# ─────────────────────────────────────────────────────────────
# 悠悠记忆系统 v4.1
# ─────────────────────────────────────────────────────────────

class YouyouMemory:
    """悠悠记忆系统 v4.1"""
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = os.path.expanduser('~/.openclaw/workspace')
        
        self.workspace = Path(workspace_path)
        
        # 初始化组件
        self.store = SQLMemoryStore(str(self.workspace / 'memory' / 'memories.db'))
        self.hooks = MemoryHooks()
        self.evolving = EvolvingMemory(self.store)
        self.search_engine = TraceableSearch(self.store)
        
        # 注册默认 Hooks
        self._register_default_hooks()
        
        print("✅ 悠悠记忆系统 v4.1 初始化完成")
    
    def _register_default_hooks(self):
        """注册默认 Hooks"""
        self.hooks.register(extract_entities)
        self.hooks.register(extract_preferences)
        self.hooks.register(extract_facts)
    
    def add_memory(self, content: str, category: str = "general", 
                   scope: str = MemoryScope.USER, **kwargs) -> str:
        """添加记忆"""
        memory = {
            "content": content,
            "category": category,
            "scope": scope,
            **kwargs
        }
        
        memory_id = self.store.add(memory)
        print(f"✅ 记忆已添加：{memory_id}")
        return memory_id
    
    def auto_capture(self, message: str, metadata: Dict = None) -> List[str]:
        """
        自动捕获记忆（Hooks）
        
        Args:
            message: 用户消息
            metadata: 元数据
        
        Returns:
            捕获的记忆 ID 列表
        """
        memories = self.hooks.on_message(message, metadata or {})
        
        captured_ids = []
        for memory in memories:
            memory_id = self.store.add(memory)
            captured_ids.append(memory_id)
        
        if captured_ids:
            print(f"🎯 自动捕获 {len(captured_ids)} 条记忆")
        
        return captured_ids
    
    def search(self, query: str, **kwargs) -> Tuple[List[Dict], Dict]:
        """
        搜索记忆
        
        Returns:
            (结果列表，追踪信息)
        """
        results, trace = self.search_engine.search(query, **kwargs)
        
        # 记录使用（提升适应度）
        for result in results:
            self.evolving.record_usage(result["id"], success=True)
        
        return results, trace
    
    def forget_low_fitness(self, threshold: float = 0.2) -> int:
        """遗忘低适应度记忆"""
        low_fitness = self.store.get_low_fitness(threshold)
        
        count = 0
        for memory in low_fitness:
            self.store.delete(memory["id"])
            count += 1
        
        if count > 0:
            print(f"🍂 已遗忘 {count} 条低适应度记忆")
        
        return count
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        store_stats = self.store.get_stats()
        fitness_dist = self.evolving.get_fitness_distribution()
        
        return {
            **store_stats,
            "fitness_distribution": fitness_dist,
            "timestamp": datetime.now().isoformat()
        }

# ─────────────────────────────────────────────────────────────
# 测试
# ─────────────────────────────────────────────────────────────

def test_enhanced_memory():
    """测试增强记忆系统"""
    print("🧠 测试悠悠记忆系统 v4.1")
    print("="*60)
    
    # 创建记忆系统
    memory = YouyouMemory()
    
    # 测试 1: 添加记忆
    print("\n📝 测试 1: 添加记忆")
    memory.add_memory("用户喜欢跨境电商", category="preferences")
    memory.add_memory("用户家庭做反光马甲生意", category="facts")
    memory.add_memory("用户目标：跨境电商出海", category="facts")
    
    # 测试 2: 自动捕获
    print("\n🎯 测试 2: 自动捕获")
    memory.auto_capture("我叫小明，喜欢编程")
    memory.auto_capture("我希望学习 Python")
    
    # 测试 3: 搜索
    print("\n🔍 测试 3: 搜索")
    results, trace = memory.search("电商")
    print(f"找到 {len(results)} 条结果")
    
    # 显示追踪
    print("\n📊 检索追踪:")
    for step in trace["steps"]:
        print(f"  Step {step['step']}: {step['action']} ({step['duration_ms']:.1f}ms)")
    
    # 测试 4: 统计
    print("\n📈 测试 4: 统计信息")
    stats = memory.get_stats()
    print(f"  总记忆数：{stats['total']}")
    print(f"  平均适应度：{stats['avg_fitness']:.2f}")
    print(f"  适应度分布：{stats['fitness_distribution']}")
    
    # 测试 5: 遗忘
    print("\n🍂 测试 5: 遗忘低适应度记忆")
    # 先模拟一些失败使用
    for i in range(10):
        memory.evolving.record_usage(f"mem_test_{i}", success=False)
    
    forgotten = memory.forget_low_fitness(threshold=0.2)
    print(f"  遗忘数量：{forgotten}")
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_enhanced_memory()

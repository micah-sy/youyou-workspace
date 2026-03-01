#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌳 悠悠记忆树可视化
Memory Tree Visualization for Youyou Memory System

让知识像树一样生长。
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# 颜色定义
class Colors:
    GREEN = '\033[92m'      # 🌿 绿叶
    YELLOW = '\033[93m'     # 🍂 黄叶
    RED = '\033[91m'        # 🍁 枯叶
    GRAY = '\033[90m'       # 🪨 土壤
    BLUE = '\033[94m'       # 📊 信息
    RESET = '\033[0m'
    BOLD = '\033[1m'

# 置信度阈值
THRESHOLD_GREEN = 0.8   # 绿叶
THRESHOLD_YELLOW = 0.5  # 黄叶
THRESHOLD_RED = 0.3     # 枯叶

class MemoryTree:
    """记忆树可视化"""
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = os.path.expanduser('~/.openclaw/workspace')
        self.workspace = Path(workspace_path)
        self.memory_dir = self.workspace / 'memory'
        self.layer2_active = self.memory_dir / 'layer2' / 'active'
        self.layer2_archive = self.memory_dir / 'layer2' / 'archive'
        
    def load_facts(self) -> List[Dict]:
        """加载 facts.jsonl"""
        facts_file = self.layer2_active / 'facts.jsonl'
        facts = []
        if facts_file.exists():
            with open(facts_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            facts.append(json.loads(line))
                        except:
                            pass
        return facts
    
    def load_beliefs(self) -> List[Dict]:
        """加载 beliefs.jsonl"""
        beliefs_file = self.layer2_active / 'beliefs.jsonl'
        beliefs = []
        if beliefs_file.exists():
            with open(beliefs_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            beliefs.append(json.loads(line))
                        except:
                            pass
        return beliefs
    
    def load_summaries(self) -> List[Dict]:
        """加载 summaries.jsonl"""
        summaries_file = self.layer2_active / 'summaries.jsonl'
        summaries = []
        if summaries_file.exists():
            with open(summaries_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            summaries.append(json.loads(line))
                        except:
                            pass
        return summaries
    
    def classify_leaf(self, score: float) -> str:
        """根据分数分类叶子"""
        if score >= THRESHOLD_GREEN:
            return 'green'
        elif score >= THRESHOLD_YELLOW:
            return 'yellow'
        elif score >= THRESHOLD_RED:
            return 'red'
        else:
            return 'gray'
    
    def get_leaf_icon(self, category: str) -> str:
        """获取叶子图标"""
        icons = {
            'green': '🌿',
            'yellow': '🍂',
            'red': '🍁',
            'gray': '🪨'
        }
        return icons.get(category, '🍃')
    
    def get_color(self, category: str) -> str:
        """获取颜色代码"""
        colors = {
            'green': Colors.GREEN,
            'yellow': Colors.YELLOW,
            'red': Colors.RED,
            'gray': Colors.GRAY
        }
        return colors.get(category, Colors.RESET)
    
    def calculate_health(self, items: List[Dict]) -> float:
        """计算健康度（绿叶比例）"""
        if not items:
            return 0.0
        green_count = sum(1 for item in items if self.classify_leaf(item.get('score', 0)) == 'green')
        return (green_count / len(items)) * 100
    
    def visualize(self) -> str:
        """生成树的可视化"""
        # 加载所有记忆
        facts = self.load_facts()
        beliefs = self.load_beliefs()
        summaries = self.load_summaries()
        
        # 分类统计
        all_items = facts + beliefs + summaries
        categories = {'green': 0, 'yellow': 0, 'red': 0, 'gray': 0}
        
        for item in all_items:
            cat = self.classify_leaf(item.get('score', 0))
            categories[cat] += 1
        
        total = len(all_items)
        health = self.calculate_health(all_items) if total > 0 else 0
        
        # 生成可视化
        output = []
        output.append(f"{Colors.BOLD}{Colors.BLUE}🌳 悠悠记忆树 (Youyou Memory Tree){Colors.RESET}")
        output.append(f"{Colors.BLUE}│{Colors.RESET}")
        output.append(f"{Colors.BLUE}├──{Colors.RESET} 📊 健康度：{Colors.GREEN if health >= 70 else Colors.YELLOW if health >= 50 else Colors.RED}{health:.1f}%{Colors.RESET}")
        output.append(f"{Colors.BLUE}├──{Colors.RESET} 🍃 总叶子：{total}")
        output.append(f"{Colors.BLUE}│   {Colors.BLUE}├──{Colors.RESET} {self.get_leaf_icon('green')} 绿叶：{Colors.GREEN}{categories['green']}{Colors.RESET}")
        output.append(f"{Colors.BLUE}│   {Colors.BLUE}├──{Colors.RESET} {self.get_leaf_icon('yellow')} 黄叶：{Colors.YELLOW}{categories['yellow']}{Colors.RESET}")
        output.append(f"{Colors.BLUE}│   {Colors.BLUE}├──{Colors.RESET} {self.get_leaf_icon('red')} 枯叶：{Colors.RED}{categories['red']}{Colors.RESET}")
        output.append(f"{Colors.BLUE}│   {Colors.BLUE}└──{Colors.RESET} {self.get_leaf_icon('gray')} 土壤：{Colors.GRAY}{categories['gray']}{Colors.RESET}")
        output.append(f"{Colors.BLUE}│{Colors.RESET}")
        
        # 按类型细分
        output.append(f"{Colors.BLUE}├──{Colors.RESET} 📁 Facts: {len(facts)} 条")
        output.append(f"{Colors.BLUE}│   {Colors.BLUE}└──{Colors.RESET} {self.get_leaf_icon('green')} {sum(1 for f in facts if self.classify_leaf(f.get('score', 0)) == 'green')} "
                     f"{self.get_leaf_icon('yellow')} {sum(1 for f in facts if self.classify_leaf(f.get('score', 0)) == 'yellow')} "
                     f"{self.get_leaf_icon('red')} {sum(1 for f in facts if self.classify_leaf(f.get('score', 0)) == 'red')} "
                     f"{self.get_leaf_icon('gray')} {sum(1 for f in facts if self.classify_leaf(f.get('score', 0)) == 'gray')}")
        
        output.append(f"{Colors.BLUE}├──{Colors.RESET} 💭 Beliefs: {len(beliefs)} 条")
        output.append(f"{Colors.BLUE}│   {Colors.BLUE}└──{Colors.RESET} {self.get_leaf_icon('green')} {sum(1 for b in beliefs if self.classify_leaf(b.get('score', 0)) == 'green')} "
                     f"{self.get_leaf_icon('yellow')} {sum(1 for b in beliefs if self.classify_leaf(b.get('score', 0)) == 'yellow')} "
                     f"{self.get_leaf_icon('red')} {sum(1 for b in beliefs if self.classify_leaf(b.get('score', 0)) == 'red')} "
                     f"{self.get_leaf_icon('gray')} {sum(1 for b in beliefs if self.classify_leaf(b.get('score', 0)) == 'gray')}")
        
        output.append(f"{Colors.BLUE}└──{Colors.RESET} 📝 Summaries: {len(summaries)} 条")
        output.append(f"{Colors.BLUE}    {Colors.BLUE}└──{Colors.RESET} {self.get_leaf_icon('green')} {sum(1 for s in summaries if self.classify_leaf(s.get('score', 0)) == 'green')} "
                     f"{self.get_leaf_icon('yellow')} {sum(1 for s in summaries if self.classify_leaf(s.get('score', 0)) == 'yellow')} "
                     f"{self.get_leaf_icon('red')} {sum(1 for s in summaries if self.classify_leaf(s.get('score', 0)) == 'red')} "
                     f"{self.get_leaf_icon('gray')} {sum(1 for s in summaries if self.classify_leaf(s.get('score', 0)) == 'gray')}")
        
        # 归档池统计
        archive_facts = 0
        archive_beliefs = 0
        if (self.layer2_archive / 'facts.jsonl').exists():
            with open(self.layer2_archive / 'facts.jsonl', 'r', encoding='utf-8') as f:
                archive_facts = sum(1 for line in f if line.strip() and not line.startswith('#'))
        if (self.layer2_archive / 'beliefs.jsonl').exists():
            with open(self.layer2_archive / 'beliefs.jsonl', 'r', encoding='utf-8') as f:
                archive_beliefs = sum(1 for line in f if line.strip() and not line.startswith('#'))
        
        output.append(f"{Colors.BLUE}│{Colors.RESET}")
        output.append(f"{Colors.BLUE}└──{Colors.RESET} 🗄️ 归档池：{archive_facts + archive_beliefs} 条 (Facts: {archive_facts}, Beliefs: {archive_beliefs})")
        
        return '\n'.join(output)
    
    def print_tree(self):
        """打印树"""
        print(self.visualize())
    
    def save_report(self, output_path: str = None):
        """保存报告"""
        if output_path is None:
            output_path = self.memory_dir / 'tree-report.md'
        
        report = f"""# 🌳 悠悠记忆树健康报告

**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 树的状态

```
{self.visualize()}
```

## 详细说明

### 🌿 绿叶 (score >= 0.8)
- 状态：健康，经常使用
- 衰减：慢
- 建议：继续保持

### 🍂 黄叶 (0.5 <= score < 0.8)
- 状态：亚健康，使用频率下降
- 衰减：中等
- 建议：增加使用频率

### 🍁 枯叶 (0.3 <= score < 0.5)
- 状态：危险，即将归档
- 衰减：快
- 建议：尽快使用或归档

### 🪨 土壤 (score < 0.3)
- 状态：已归档
- 处理：精华提取，化作养分
- 建议：可被新知识引用

---

_让知识像树一样生长。_ 🌳
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"{Colors.GREEN}✅ 报告已保存到：{output_path}{Colors.RESET}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='🌳 悠悠记忆树可视化')
    parser.add_argument('--workspace', '-w', type=str, help='工作区路径')
    parser.add_argument('--output', '-o', type=str, help='保存报告路径')
    parser.add_argument('--quiet', '-q', action='store_true', help='安静模式（不打印）')
    
    args = parser.parse_args()
    
    tree = MemoryTree(args.workspace)
    
    if not args.quiet:
        tree.print_tree()
    
    if args.output:
        tree.save_report(args.output)


if __name__ == '__main__':
    main()

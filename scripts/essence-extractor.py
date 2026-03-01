#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💎 记忆精华提取
Essence Extractor for Memory System

从即将归档的记忆中提取精华，化作新知识的养分。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class EssenceExtractor:
    """记忆精华提取器"""
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = os.path.expanduser('~/.openclaw/workspace')
        self.workspace = Path(workspace_path)
        self.memory_dir = self.workspace / 'memory'
        self.layer2_active = self.memory_dir / 'layer2' / 'active'
        self.layer2_archive = self.memory_dir / 'layer2' / 'archive'
        self.essence_file = self.memory_dir / 'essence.jsonl'
        
    def load_low_score_items(self, threshold: float = 0.3) -> List[Dict]:
        """加载低分项目（即将归档）"""
        low_score_items = []
        
        for file_name in ['facts.jsonl', 'beliefs.jsonl', 'summaries.jsonl']:
            file_path = self.layer2_active / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                item = json.loads(line)
                                if item.get('score', 1.0) < threshold:
                                    low_score_items.append(item)
                            except:
                                pass
        
        return low_score_items
    
    def extract_essence(self, item: Dict) -> Optional[str]:
        """从单个项目中提取精华"""
        content = item.get('content', '')
        item_type = item.get('type', 'unknown')
        entities = item.get('entities', [])
        
        if not content:
            return None
        
        # 精华提取规则
        essence_lines = []
        
        # 1. 提取核心内容（前 100 字）
        core = content[:100] if len(content) > 100 else content
        essence_lines.append(f"核心：{core}")
        
        # 2. 提取关键实体
        if entities:
            essence_lines.append(f"关键：{', '.join(entities[:5])}")
        
        # 3. 添加引用标记
        essence_lines.append(f"来源：{item.get('id', 'unknown')}")
        
        return ' | '.join(essence_lines)
    
    def save_essence(self, essence_entries: List[Dict]):
        """保存精华到文件"""
        with open(self.essence_file, 'a', encoding='utf-8') as f:
            for entry in essence_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def run(self, dry_run: bool = False) -> Dict:
        """运行精华提取"""
        print("💎 开始提取记忆精华...")
        
        low_score_items = self.load_low_score_items()
        
        if not low_score_items:
            print("✅ 没有需要提取精华的记忆")
            return {'extracted': 0, 'saved': 0}
        
        print(f"📊 发现 {len(low_score_items)} 条低分记忆")
        
        essence_entries = []
        for item in low_score_items:
            essence = self.extract_essence(item)
            if essence:
                entry = {
                    'id': f"e_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{item.get('id', 'unknown')}",
                    'source_id': item.get('id'),
                    'source_type': item.get('type'),
                    'essence': essence,
                    'original_score': item.get('score'),
                    'extracted_at': datetime.now().isoformat(),
                    'entities': item.get('entities', [])
                }
                essence_entries.append(entry)
                
                if not dry_run:
                    print(f"  ✅ 提取：{item.get('content', '')[:50]}...")
                else:
                    print(f"  🔍 预览：{essence[:80]}...")
        
        if not dry_run and essence_entries:
            self.save_essence(essence_entries)
            print(f"✅ 已保存 {len(essence_entries)} 条精华到 essence.jsonl")
        
        return {
            'extracted': len(essence_entries),
            'saved': len(essence_entries) if not dry_run else 0
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='💎 记忆精华提取')
    parser.add_argument('--workspace', '-w', type=str, help='工作区路径')
    parser.add_argument('--dry-run', '-n', action='store_true', help='预览模式（不保存）')
    
    args = parser.parse_args()
    
    extractor = EssenceExtractor(args.workspace)
    result = extractor.run(dry_run=args.dry_run)
    
    print(f"\n📊 结果：提取 {result['extracted']} 条，保存 {result['saved']} 条")


if __name__ == '__main__':
    main()

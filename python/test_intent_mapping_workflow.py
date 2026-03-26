#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
intent_mapping_workflow 本地测试脚本
用于验证意图配置接口是否可被 HiAgent 工作流正常读取。
"""

import json

import intent_mapping_workflow


TEST_CASES = [
    {
        "name": "读取启用意图列表",
        "params": {
            "action": "get_enabled_intents"
        }
    },
    {
        "name": "读取全部意图列表",
        "params": {
            "action": "get_all_intents"
        }
    },
    {
        "name": "按编码读取单个意图",
        "params": {
            "action": "get_intent_by_code",
            "intent_code": "view_items"
        }
    },
    {
        "name": "读取映射规则",
        "params": {
            "action": "get_mapping_rules"
        }
    }
]


print("=" * 60)
print("intent_mapping_workflow 测试开始")
print("=" * 60)
print()

for index, test_case in enumerate(TEST_CASES, 1):
    params = test_case["params"]
    print("=" * 60)
    print(f"测试{index}：{test_case['name']}")
    print("=" * 60)
    print("入参:", params)

    result = intent_mapping_workflow.handler(params)
    print("输出结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()

print("=" * 60)
print("测试完成")
print("=" * 60)

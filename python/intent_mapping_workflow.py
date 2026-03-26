#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HiAgent 意图配置工作流接口：
1. 在 Python 脚本内维护正式意图配置；
2. 按 action 返回全部意图、启用意图或单个意图；
3. 作为工作流接口节点给大模型节点或选择器节点提供配置数据。

说明：
- Python 不负责意图识别，只负责管理和暴露意图配置；
- 正式识别由 HiAgent 大模型节点完成；
- 该脚本解决 HiAgent 数据库节点不适合直接维护 JSON 配置的问题。
"""


INTENT_CONFIG = {
    "version": "2.0.0",
    "updated_at": "2026-03-26",
    "source_of_truth": "docs/来伊份 AI 导购助手 HiAgent 架构文档 V1.0.pdf 1.3 / 2.0 / 2.3",
    "default_clarify_question": "请问您现在是想让我帮您推荐商品、查看购物车、加入购物车、确认订单，还是查询订单？",
    "intents": [
        {
            "intent_name_cn": "商品推荐",
            "intent_code": "view_items",
            "target_agent": "商推Agent",
            "collaboration_mode": "single",
            "description": "用户希望获得商品推荐或场景推荐。",
            "examples": ["帮我推荐点零食", "送长辈买什么", "有什么适合追剧吃的"],
            "priority": 100,
            "enabled": True
        },
        {
            "intent_name_cn": "查询购物车",
            "intent_code": "view_shop_cart",
            "target_agent": "交易Agent",
            "collaboration_mode": "single",
            "description": "用户希望查看当前购物车商品列表。",
            "examples": ["看看我的购物车", "购物车里有什么", "查询购物车"],
            "priority": 95,
            "enabled": True
        },
        {
            "intent_name_cn": "添加购物车",
            "intent_code": "add_shop_cart",
            "target_agent": "交易Agent",
            "collaboration_mode": "serial",
            "description": "用户希望将商品加入购物车。",
            "examples": ["这个加购物车", "把刚才推荐的都加上", "来两件这个"],
            "priority": 100,
            "enabled": True
        },
        {
            "intent_name_cn": "删除购物车",
            "intent_code": "del_shop_cart",
            "target_agent": "交易Agent",
            "collaboration_mode": "single",
            "description": "用户希望删除购物车中的某个商品。",
            "examples": ["把这个从购物车删掉", "删除购物车里的薯片", "移除这件商品"],
            "priority": 85,
            "enabled": True
        },
        {
            "intent_name_cn": "清空购物车",
            "intent_code": "clear_shop_cart",
            "target_agent": "交易Agent",
            "collaboration_mode": "single",
            "description": "用户希望清空购物车中的全部商品。",
            "examples": ["清空购物车", "把购物车都删了", "全部不要了"],
            "priority": 80,
            "enabled": True
        },
        {
            "intent_name_cn": "确认订单",
            "intent_code": "confirm_order",
            "target_agent": "交易Agent",
            "collaboration_mode": "serial",
            "description": "用户确认商品信息后，希望进入下单确认流程。",
            "examples": ["确认订单", "就这些，确认一下", "去确认订单"],
            "priority": 90,
            "enabled": True
        },
        {
            "intent_name_cn": "立即下单",
            "intent_code": "place_order_oow",
            "target_agent": "交易Agent",
            "collaboration_mode": "serial",
            "description": "用户希望搜索商品并直接下单。",
            "examples": ["直接下单", "现在就买", "立即下单"],
            "priority": 100,
            "enabled": True
        },
        {
            "intent_name_cn": "取消订单",
            "intent_code": "cancel_order",
            "target_agent": "交易Agent",
            "collaboration_mode": "single",
            "description": "用户希望取消指定订单。",
            "examples": ["取消这个订单", "帮我退掉这单", "我要取消订单"],
            "priority": 75,
            "enabled": True
        },
        {
            "intent_name_cn": "查询订单",
            "intent_code": "query_order",
            "target_agent": "交易Agent",
            "collaboration_mode": "single",
            "description": "用户希望查询订单信息，包含订单状态或订单详情。",
            "examples": ["我的订单", "查询订单", "订单状态怎么样"],
            "priority": 95,
            "enabled": True
        },
        {
            "intent_name_cn": "知识问答",
            "intent_code": "knowledge_quiz",
            "target_agent": "问答Agent",
            "collaboration_mode": "single",
            "description": "用户希望咨询 FAQ、商品知识或规则问题。",
            "examples": ["会员有什么权益", "这个配料是什么", "运费怎么算"],
            "priority": 85,
            "enabled": True
        },
        {
            "intent_name_cn": "闲聊回复",
            "intent_code": "casual_reply",
            "target_agent": "闲聊Agent",
            "collaboration_mode": "single",
            "description": "用户进行非业务闲聊、寒暄或感谢。",
            "examples": ["你好", "谢谢", "在吗"],
            "priority": 0,
            "enabled": True
        }
    ],
    "mapping_rules": [
        "intent_code 严格采用架构文档 2.0 定义。",
        "target_agent 严格采用架构文档 1.3 定义。",
        "collaboration_mode 严格采用架构文档 2.3 定义。",
        "交易域动作统一由交易Agent承接，不再拆分购物车Agent或订单Agent。",
        "FAQ、商品知识、规则咨询统一收敛到 knowledge_quiz -> 问答Agent。",
        "闲聊统一收敛到 casual_reply -> 闲聊Agent。"
    ]
}


def clean_param(value):
    """
    通用入参清洗函数：
    ① Python None → 空字符串；
    ② 列表类型逐项清洗；
    ③ 字符串去首尾空格；
    ④ "NULL"/"null"/"Null" → 空字符串。
    """
    if value is None:
        return ""

    if isinstance(value, list):
        cleaned_list = []
        for item in value:
            cleaned_item = clean_param(item)
            if cleaned_item:
                cleaned_list.append(cleaned_item)
        return cleaned_list if cleaned_list else ""

    str_value = str(value).strip()
    if str_value.upper() == "NULL":
        return ""
    return str_value


def load_config():
    """读取完整意图配置。"""
    return INTENT_CONFIG


def list_enabled_intents(config_data):
    """返回 enabled=True 的意图列表。"""
    return [item for item in config_data.get("intents", []) if item.get("enabled")]


def get_intent_by_code(config_data, intent_code):
    """按 intent_code 查询单个意图。"""
    for item in config_data.get("intents", []):
        if item.get("intent_code") == intent_code:
            return item
    return None


def handler(params):
    """
    处理意图配置读取请求。

    支持 action：
    - get_enabled_intents：返回启用中的意图列表
    - get_all_intents：返回全部意图列表
    - get_intent_by_code：按 intent_code 返回单个意图
    - get_mapping_rules：返回 mapping_rules
    """
    try:
        if not isinstance(params, dict):
            raise ValueError("入参必须为字典格式")

        config_data = load_config()
        action = clean_param(params.get("action")) or "get_enabled_intents"

        if action == "get_enabled_intents":
            intents = list_enabled_intents(config_data)
            return {
                "intents": intents,
                "default_clarify_question": config_data.get("default_clarify_question", "")
            }

        if action == "get_all_intents":
            return {
                "intents": config_data.get("intents", []),
                "default_clarify_question": config_data.get("default_clarify_question", "")
            }

        if action == "get_intent_by_code":
            intent_code = clean_param(params.get("intent_code"))
            if not intent_code:
                raise ValueError("action=get_intent_by_code 时 intent_code 不能为空")

            intent_item = get_intent_by_code(config_data, intent_code)
            return intent_item or {}

        if action == "get_mapping_rules":
            return {
                "mapping_rules": config_data.get("mapping_rules", []),
                "default_clarify_question": config_data.get("default_clarify_question", "")
            }

        raise ValueError(
            "不支持的 action。仅支持 get_enabled_intents / get_all_intents / "
            "get_intent_by_code / get_mapping_rules"
        )

    except Exception as error:
        return {
            "error": str(error)
        }

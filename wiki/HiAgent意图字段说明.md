# HiAgent意图字段说明

本文用于说明来伊份导购助手中与意图识别相关的核心字段，适合直接放入知识库。

## 1. 前置节点输出字段

前置节点为 `intent_mapping_workflow`，职责是返回可供大模型识别使用的标准意图配置，不直接做意图判断。

### `intents`

- 含义：可被识别的标准意图列表
- 类型：`array<object>`
- 来源：`python/intent_mapping_workflow.py`
- 用途：作为大模型意图识别的候选范围

单个 `intent` 结构如下：

### `intent_name_cn`

- 含义：意图中文名称
- 类型：`string`
- 示例：`商品推荐`

### `intent_code`

- 含义：意图英文编码，系统内唯一标识
- 类型：`string`
- 示例：`view_items`
- 说明：必须严格采用架构文档 2.0 定义

### `target_agent`

- 含义：该意图对应的目标智能体
- 类型：`string`
- 可选值：`商推Agent`、`交易Agent`、`问答Agent`、`闲聊Agent`

### `collaboration_mode`

- 含义：该意图默认协作模式
- 类型：`string`
- 可选值：`single`、`serial`、`parallel`、`nested`

### `description`

- 含义：意图业务说明
- 类型：`string`
- 用途：帮助模型理解该意图边界

### `examples`

- 含义：该意图的典型用户表达示例
- 类型：`array<string>`
- 用途：增强模型对口语化表达的识别能力

### `priority`

- 含义：意图优先级
- 类型：`number`
- 用途：在多意图同时命中时辅助排序

### `enabled`

- 含义：意图是否启用
- 类型：`boolean`
- 用途：控制该意图是否参与当前识别

### `default_clarify_question`

- 含义：默认澄清话术
- 类型：`string`
- 用途：当输入模糊或无法稳定判断主意图时使用

## 2. 大模型意图识别输出字段

大模型节点基于 `intents` 做识别，输出结构化意图分析结果。

### `primary_intent_code`

- 含义：当前轮最优先执行的主意图编码
- 类型：`string`
- 示例：`add_shop_cart`
- 说明：只能从 `intents` 列表中选择

### `need_clarify`

- 含义：是否需要澄清
- 类型：`boolean`
- 示例：`true` / `false`
- 说明：当输入不完整、指代不明、多意图先后无法判断时返回 `true`

### `clarify_question`

- 含义：澄清问题
- 类型：`string`
- 示例：`请问您现在是想让我帮您推荐商品、查看购物车、加入购物车、确认订单，还是查询订单？`
- 说明：`need_clarify=false` 时应返回空字符串

### `reason_text`

- 含义：整体判断原因
- 类型：`string`
- 用途：解释为什么选定当前主意图

### `intents_analysis`

- 含义：完整意图分析列表
- 类型：`array<object>`
- 用途：保留本轮识别到的全部意图结构，支持多意图分析、日志留存和后续工作流扩展

单个 `intents_analysis` 项结构如下：

### `intent_name_cn`

- 含义：该意图的中文名称
- 类型：`string`

### `intent_code`

- 含义：该意图的英文编码
- 类型：`string`

### `target_agent`

- 含义：该意图对应的目标智能体
- 类型：`string`

### `collaboration_mode`

- 含义：该意图建议使用的协作模式
- 类型：`string`

### `rank`

- 含义：意图优先级顺位
- 类型：`number`
- 说明：`1` 表示最优先，且应与 `primary_intent_code` 对应

### `reason_text`

- 含义：该意图命中的原因
- 类型：`string`

## 3. 使用建议

- 当前轮路由只使用 `primary_intent_code` 和 `need_clarify`
- `intents_analysis` 当前只做记录、调试和后续扩展，不建议首版直接参与分支决策
- 所有 `intent_code`、`target_agent`、`collaboration_mode` 都必须与前置节点配置一致

## 4. 示例

```json
{
  "primary_intent_code": "add_shop_cart",
  "need_clarify": false,
  "clarify_question": "",
  "reason_text": "用户同时表达了加购和下单诉求，当前第一执行步是加购。",
  "intents_analysis": [
    {
      "intent_name_cn": "添加购物车",
      "intent_code": "add_shop_cart",
      "target_agent": "交易Agent",
      "collaboration_mode": "serial",
      "rank": 1,
      "reason_text": "用户明确表达了将商品加入购物车。"
    },
    {
      "intent_name_cn": "立即下单",
      "intent_code": "place_order_oow",
      "target_agent": "交易Agent",
      "collaboration_mode": "serial",
      "rank": 2,
      "reason_text": "用户同时表达了后续下单诉求，但执行顺序在加购之后。"
    }
  ]
}
```

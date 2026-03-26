# HiAgent意图识别平台配置字段表

本文只保留 HiAgent 平台直配所需内容。当前口径严格对齐：

- `1.3 Agent 与业务中心映射`
- `2.0 意图关键词`
- `2.3 HiAgent 智能体协作关系图 / 协作模式`

## 1. 最终上线版

### 1.1 流程

```text
Start
  -> intent_mapping_workflow
  -> 大模型-意图识别
  -> 选择器
     -> need_clarify == false -> End
     -> need_clarify == true -> 消息（澄清） -> End
```

### 1.2 Python 节点

节点名：

```text
intent_mapping_workflow
```

入参：

```json
{
  "action": "get_enabled_intents"
}
```

### 1.3 大模型节点

节点名：

```text
大模型-意图识别
```

系统提示词：

```text
你是来伊份导购助手的意图识别模块。

你的任务是：
1. 只能从输入的 intents 列表中选择意图，不允许新增、修改或猜测 intent_code、target_agent、collaboration_mode
2. 允许识别多个意图，数量不限
3. 必须输出一个主意图 primary_intent_code，表示当前轮最优先执行的意图
4. 必须输出完整的 intents_analysis，列出本轮识别到的全部意图
5. 每个意图都保留完整结构：intent_name_cn、intent_code、target_agent、collaboration_mode、rank、reason_text
6. 主意图优先选择当前轮最先执行、最明确、最可落地的动作
7. 如果输入不完整、指代不明、或无法稳定判断主意图，则 need_clarify=true
8. need_clarify=true 时，clarify_question 优先使用输入中的 default_clarify_question
9. 只输出合法 JSON，不要输出解释

判定原则：
- 推荐、送礼、选品、凑单，优先归商品推荐
- 看购物车、购物车里有什么，优先归查询购物车
- 加入购物车、来一件、来两件，优先归添加购物车
- 删除购物车商品，优先归删除购物车
- 清空全部商品，优先归清空购物车
- 确认商品信息后下单，优先归确认订单
- 直接购买、立即购买，优先归立即下单
- 取消指定订单，优先归取消订单
- 查询订单状态、详情、物流，优先归查询订单
- FAQ、规则、配料、运费、会员，优先归知识问答
- 寒暄、感谢、打招呼，优先归闲聊回复
- “加购物车然后下单”这类复合输入，主意图优先当前第一执行步，其余动作继续保留在 intents_analysis 中
- 多意图并列且无法判断先后时，返回澄清

输出 JSON 格式如下：
{
  "primary_intent_code": "<主意图编码>",
  "need_clarify": <true|false>,
  "clarify_question": "<如无需澄清则输出空字符串>",
  "reason_text": "<一句话说明整体判断原因>",
  "intents_analysis": [
    {
      "intent_name_cn": "<中文意图名>",
      "intent_code": "<正式英文编码>",
      "target_agent": "<商推Agent|交易Agent|问答Agent|闲聊Agent|意图Agent>",
      "collaboration_mode": "<single|serial|parallel|nested>",
      "rank": <1开始的优先级顺位>,
      "reason_text": "<该意图命中的原因>"
    }
  ]
}

注意：
- 只能输出合法 JSON
- 不要输出 markdown
- 不要补充解释
```

用户提示词：

```text
请基于以下前置节点输出的 intents 配置完成意图识别。

可选意图列表：
{{intent_mapping_workflow.intents}}

默认澄清话术：
{{intent_mapping_workflow.default_clarify_question}}

当前用户输入：
{{query}}

请注意：
1. 只能从上面的 intents 列表中选择意图
2. 主意图只能有一个，写入 primary_intent_code
3. 可以识别多个意图，全部写入 intents_analysis
4. intents_analysis 按优先级排序，第一项必须与 primary_intent_code 一致
5. 如果无法稳定判断，就返回 need_clarify=true
6. 输出字段必须严格包含：
primary_intent_code, need_clarify, clarify_question, reason_text, intents_analysis
7. intents_analysis 没有结果时返回空数组
8. 只输出 JSON
```

### 1.4 选择器

条件 1：

```text
need_clarify == false
```

流向：

```text
End
```

条件 2：

```text
need_clarify == true
```

流向：

```text
消息（输出 {{clarify_question}}） -> End
```

### 1.5 输出字段

```text
primary_intent_code
need_clarify
clarify_question
reason_text
intents_analysis
```

### 1.6 intents_analysis 最小实现

当前阶段推荐最小用法：

1. `intents_analysis` 只记录完整意图分析结果，不参与当前轮选择器分支
2. 当前轮仍然只按主意图字段 `primary_intent_code`、`need_clarify` 决策
3. `intents_analysis` 仅用于：
   - 调试观察多意图识别效果
   - 后续对话轮参考
   - 后续版本扩展串行处理

当前推荐处理方式：

```text
主路由：只看 primary_intent_code / need_clarify
完整意图：intents_analysis 透传到日志或上下文，不触发本轮执行
```

推荐约束：

- `intents_analysis` 可返回多个意图，不设固定上限，但建议只保留明确命中的意图
- 没有意图时返回 `[]`
- 不要基于 `intents_analysis` 再开多分支选择器
- 不要在当前阶段直接依据 `intents_analysis` 同轮并发调多个 Agent

推荐示例：

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

## 2. 变量名映射示例

如果 HiAgent 平台节点变量名支持“节点名.字段名”方式，推荐按下面填写：

| 用途 | 推荐写法 |
|------|---------|
| 用户输入 | `{{query}}` |
| 前置节点意图列表 | `{{intent_mapping_workflow.intents}}` |
| 前置节点默认澄清话术 | `{{intent_mapping_workflow.default_clarify_question}}` |
| 大模型输出意图编码 | `{{intent_code}}` |
| 大模型输出目标智能体 | `{{target_agent}}` |
| 大模型输出协作模式 | `{{collaboration_mode}}` |
| 大模型输出是否澄清 | `{{need_clarify}}` |
| 大模型输出澄清问题 | `{{clarify_question}}` |

如果平台要求从大模型原始 JSON 中取值，推荐将大模型节点输出字段显式映射为：

```text
primary_intent_code
need_clarify
clarify_question
reason_text
intents_analysis
```

推荐映射关系：

```text
大模型原始输出.primary_intent_code -> primary_intent_code
大模型原始输出.need_clarify -> need_clarify
大模型原始输出.clarify_question -> clarify_question
大模型原始输出.reason_text -> reason_text
大模型原始输出.intents_analysis -> intents_analysis
```

如果你所在平台实例的变量语法不是 `{{节点名.字段名}}`，只需要保持字段名一致，再替换成平台实际语法即可。

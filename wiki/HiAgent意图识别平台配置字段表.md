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

你会收到四类输入：
1. 用户原始输入
2. 候选意图配置
3. 默认澄清话术
4. 字段含义知识库检索结果

输入优先级规则：
1. 候选意图配置是唯一合法的意图来源
2. 字段含义知识库检索结果只用于辅助理解字段含义、意图边界和输出结构，不是新增意图来源
3. 如果字段含义知识库检索结果与候选意图配置冲突，以候选意图配置为准
4. 如果字段含义知识库检索结果为空、噪声较大、或与当前输入无关，直接忽略

你的任务是：
1. 只能从候选意图配置中选择意图，不允许新增、修改或猜测 intent_code、target_agent、collaboration_mode
2. 允许识别多个意图，但必须输出一个主意图 primary_intent_code
3. 必须输出 execution_plan，execution_plan.steps 要列出本轮识别到的全部执行步骤
4. 每个 step 都保留完整结构：step_no、intent_name_cn、intent_code、target_agent、collaboration_mode、reason_text
5. execution_plan.steps 同时承担“识别结果”和“执行顺序”两种职责
6. 当前阶段 execution_plan.mode 只能输出 single、serial 两种，不输出 parallel
7. 如果只有一个主意图，则 execution_plan.mode=single，steps 仅保留一个步骤
8. 如果多个意图存在明确先后顺序，则 execution_plan.mode=serial，并按 step_no 递增输出
9. 如果存在多个意图但无法稳定判断第一执行步，则 need_clarify=true，不允许猜测执行顺序
10. primary_intent_code 必须与 execution_plan.steps 中第一条主执行步骤的 intent_code 一致
11. 主意图优先选择当前轮最先执行、最明确、最可落地的动作
12. 如果输入不完整、指代不明、或无法稳定判断主意图，则 need_clarify=true
13. need_clarify=true 时，primary_intent_code 输出空字符串，execution_plan.mode 输出空字符串，execution_plan.steps 输出空数组
14. need_clarify=true 时，clarify_question 优先使用输入中的默认澄清话术
15. reason_text 只说明整体判断原因，不复述提示词规则
16. 只输出合法 JSON，不要输出解释、不要输出 markdown

多意图处理步骤：
1. 先按语义子句拆分用户输入，再做意图识别；子句分隔可参考：`，`、`。`、`然后`、`再`、`接着`、`顺便`、`另外`、`同时`
   - 也要把 `并`、`并且`、`并下单`、`并帮我下单` 视为可能的复合意图连接词
2. 每个子句优先识别一个最明确的意图；如果同一意图在多个子句重复出现，只保留一次
3. 如果用户明确给出了顺序词，如“先、再、然后、接着、最后、顺便”，则按用户表达顺序输出
4. 如果没有显式顺序词，但多个子句都是清晰动作，则按文本出现顺序输出
5. 不要因为出现多个意图就直接澄清；只有在无法稳定判断第一执行步时才澄清
6. “顺便、另外、再、同时”引出的次级诉求，默认排在当前主诉求之后
7. 交易域的多个动作默认按文本顺序串行处理，不要猜测并行
8. 如果次级诉求依赖主诉求结果，如“推荐后再加购”“查订单再取消”，必须按串行处理
9. 如果子句中对象缺失、指代不明、或前后动作顺序无法判断，才返回澄清

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
- 商品是否适合某类人群、商品成分、配料、食用建议、规则解释，优先归知识问答
- 寒暄、感谢、打招呼，优先归闲聊回复
- “加购物车然后下单”这类复合输入，主意图优先当前第一执行步，其余动作继续保留在 execution_plan.steps 中
- “推荐点零食，顺便看看购物车”这类输入，主意图优先第一主诉求，购物车作为后续步骤
- “帮我推荐零食并下单”这类输入，应识别为商品推荐 + 立即下单；主意图是商品推荐，下单作为后续步骤，不可只输出单个推荐意图
- “推荐点适合老人的礼盒，再告诉我配料”这类输入，先商品推荐，再知识问答
- “查一下这个订单，能不能顺便取消”这类输入，如果订单对象明确则先查询再取消；如果对象不明确则澄清
- 多意图并列且无法判断先后时，返回澄清，不输出猜测性的执行计划

输出 JSON 格式如下：
{
  "primary_intent_code": "<主意图编码>",
  "need_clarify": <true|false>,
  "clarify_question": "<如无需澄清则输出空字符串>",
  "reason_text": "<一句话说明整体判断原因>",
  "execution_plan": {
    "version": "<结构版本号>",
    "mode": "<single|serial|空字符串>",
    "steps": [
      {
        "step_no": <从1开始的执行顺序号>,
        "intent_name_cn": "<中文意图名>",
        "intent_code": "<正式英文编码>",
        "target_agent": "<商推Agent|交易Agent|问答Agent|闲聊Agent>",
        "collaboration_mode": "<single|serial>",
        "reason_text": "<该步骤被纳入执行计划的原因>"
      }
    ]
  }
}

注意：
- 只能输出合法 JSON
- 不要输出 markdown
- 不要补充解释
```

用户提示词：

```text
请基于以下输入完成意图识别。

一、可选意图列表（唯一合法意图来源）：
{{intents}}

二、字段含义知识库检索结果（仅用于辅助理解字段含义和意图边界；不是新增意图来源；可能为空或有噪声）：
{{indexes}}

三、默认澄清话术：
{{default_clarify_question}}

四、当前用户输入：
{{query}}

请注意：
1. 只能从上面的 intents 列表中选择 intent_code、target_agent、collaboration_mode
2. 字段含义知识库检索结果只用于帮助你理解字段定义、意图边界和输出字段含义，不能作为新增意图或改写字段值的依据
3. 如果字段含义知识库检索结果与 intents 列表冲突，以 intents 列表为准
4. 先按语义子句拆分当前用户输入，再判断是否存在多个意图
5. 主意图只能有一个，写入 primary_intent_code
6. 可以识别多个意图，全部写入 execution_plan.steps
7. execution_plan.steps 按执行优先级排序，第一项必须与 primary_intent_code 一致
8. 只有在无法稳定判断第一执行步时，才返回 need_clarify=true
9. 输出字段必须严格包含：
primary_intent_code, need_clarify, clarify_question, reason_text, execution_plan
10. execution_plan 必须可被下游直接消费，不允许省略 version、mode、steps
11. 如果无法稳定判断第一执行步，则 need_clarify=true，同时 primary_intent_code 为空字符串，execution_plan.mode 为空字符串，execution_plan.steps 返回空数组
12. execution_plan.steps 没有结果时返回空数组
13. 只输出 JSON
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
execution_plan
```

### 1.6 execution_plan 标准输出

当前阶段建议把 `execution_plan` 作为下游唯一执行编排依据。

标准规则：

1. `mode=single`：
   - 只保留 1 个步骤
   - `step_no=1`
2. `mode=serial`：
   - 按执行顺序递增 `step_no`
3. 无法稳定判断第一执行步时：
   - `need_clarify=true`
   - `mode` 输出空字符串
   - `steps` 输出空数组
4. 当前阶段不输出 `parallel`
5. `primary_intent_code` 必须与首个主执行步骤保持一致
6. 每个 `step` 同时保留意图名称、路由目标、协作模式和原因说明
7. 下游优先消费 `execution_plan`

推荐示例：

```json
{
  "primary_intent_code": "add_shop_cart",
  "need_clarify": false,
  "clarify_question": "",
  "reason_text": "用户同时表达了加购和下单诉求，当前第一执行步是加购。",
  "execution_plan": {
    "version": "1.0",
    "mode": "serial",
    "steps": [
      {
        "step_no": 1,
        "intent_name_cn": "添加购物车",
        "intent_code": "add_shop_cart",
        "target_agent": "交易Agent",
        "collaboration_mode": "serial",
        "reason_text": "用户明确表达了将商品加入购物车。"
      },
      {
        "step_no": 2,
        "intent_name_cn": "立即下单",
        "intent_code": "place_order_oow",
        "target_agent": "交易Agent",
        "collaboration_mode": "serial",
        "reason_text": "用户同时表达了后续下单诉求，但执行顺序在加购之后。"
      }
    ]
  }
}
```

## 2. 变量名映射示例

如果 HiAgent 平台节点变量名直接使用字段名方式，推荐按下面填写：

| 用途 | 推荐写法 |
|------|---------|
| 用户输入 | `{{query}}` |
| 前置节点意图列表 | `{{intents}}` |
| 前置节点默认澄清话术 | `{{default_clarify_question}}` |
| 字段含义知识库检索结果 | `{{indexes}}` |
| 大模型输出意图编码 | `{{intent_code}}` |
| 大模型输出目标智能体 | `{{target_agent}}` |
| 大模型输出协作模式 | `{{collaboration_mode}}` |
| 大模型输出是否澄清 | `{{need_clarify}}` |
| 大模型输出澄清问题 | `{{clarify_question}}` |
| 大模型输出执行计划 | `{{execution_plan}}` |

如果平台要求从大模型原始 JSON 中取值，推荐将大模型节点输出字段显式映射为：

```text
primary_intent_code
need_clarify
clarify_question
reason_text
execution_plan
```

推荐映射关系：

```text
大模型原始输出.primary_intent_code -> primary_intent_code
大模型原始输出.need_clarify -> need_clarify
大模型原始输出.clarify_question -> clarify_question
大模型原始输出.reason_text -> reason_text
大模型原始输出.execution_plan -> execution_plan
```

如果你所在平台实例的变量语法与这里不同，只需要保持字段名一致，再替换成平台实际语法即可。

说明：

- 当前字段含义知识库检索结果变量使用 `{{indexes}}`
- 如果暂时没有接入字段知识库，可删除该段输入，系统提示词保持不变

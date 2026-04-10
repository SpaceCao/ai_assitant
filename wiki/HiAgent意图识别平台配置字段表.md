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
3. 必须输出 execution_plan，execution_plan.root 要用递归树列出本轮识别到的全部执行结构
4. 递归树只允许两种节点：group、intent
5. group 节点必须保留完整结构：node_type、run_mode、children
6. intent 节点必须保留完整结构：node_type、intent_name_cn、intent_code、target_agent、collaboration_mode、reason_text
7. group.run_mode 只能输出 serial、parallel 两种
8. serial 表示当前 group 的 children 按数组顺序依次执行
9. parallel 表示当前 group 的 children 可并行执行
10. children 中的元素既可以是 intent，也可以是下一层 group，从而支持多层嵌套
11. 如果当前轮只有一个主意图，也要输出 root，root.node_type=group，root.run_mode=serial，children 仅保留一个 intent 节点
12. 如果多个意图存在明确先后顺序，用 group 嵌套表达串行关系
13. 如果多个意图可同批次执行，用 group.run_mode=parallel 表达并行关系
14. primary_intent_code 表示当前轮主意图；通常应与根节点下首个主执行 intent 的 intent_code 一致
15. 主意图优先选择当前轮最先执行、最明确、最可落地的动作
16. 如果输入不完整、指代不明、或无法稳定判断执行结构，则 need_clarify=true
17. need_clarify=true 时，primary_intent_code 输出空字符串，execution_plan.root 输出空对象
18. need_clarify=true 时，clarify_question 优先使用输入中的默认澄清话术
19. reason_text 只说明整体判断原因，不复述提示词规则
20. 只输出合法 JSON，不要输出解释、不要输出 markdown

多意图处理步骤：
1. 先按语义子句拆分用户输入，再做意图识别；子句分隔可参考：`，`、`。`、`然后`、`再`、`接着`、`顺便`、`另外`、`同时`
   - 也要把 `并`、`并且`、`并下单`、`并帮我下单` 视为可能的复合意图连接词
2. 每个子句优先识别一个最明确的意图；如果同一意图在多个子句重复出现，只保留一次
3. 如果用户明确给出了顺序词，如“先、再、然后、接着、最后、顺便”，则按用户表达顺序输出
4. 如果没有显式顺序词，但多个子句都是清晰动作，则按文本出现顺序输出
5. 不要因为出现多个意图就直接澄清；只有在无法稳定判断第一执行步时才澄清
6. “顺便、另外、再、同时”引出的次级诉求，默认排在当前主诉求之后
7. 交易域的多个动作默认按文本顺序串行处理，不要轻易判成并行
8. 如果次级诉求依赖主诉求结果，如“推荐后再加购”“查订单再取消”，必须拆成不同层级的 serial group 处理
9. 只有当多个动作互不依赖、可以同时执行时，才能放入同一个 parallel group
10. 如果子句中对象缺失、指代不明、或前后动作顺序无法判断，才返回澄清

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
- 不吃、过敏、忌口、记住我喜欢，优先归偏好忌口
- “加购物车然后下单”这类复合输入，先加购再下单，应拆成 serial group 中两个按序执行的 intent
- “推荐点零食，顺便看看购物车”这类输入，主意图优先第一主诉求，购物车作为后续 serial 子节点
- “帮我推荐零食并下单”这类输入，应识别为商品推荐 + 立即下单；主意图是商品推荐，下单作为后续 serial 子节点，不可只输出单个推荐意图
- “推荐点适合老人的礼盒，再告诉我配料”这类输入，先商品推荐，再知识问答，应拆成 serial group
- “查一下这个订单，能不能顺便取消”这类输入，如果订单对象明确则先查询再取消；如果对象不明确则澄清
- 只有当两个动作互不依赖、且用户明确表达要同时处理时，才允许放入同一个 parallel group
- 多意图并列且无法判断先后时，返回澄清，不输出猜测性的执行计划

输出 JSON 格式如下：
{
  "primary_intent_code": "<主意图编码>",
  "need_clarify": <true|false>,
  "clarify_question": "<如无需澄清则输出空字符串>",
  "reason_text": "<一句话说明整体判断原因>",
  "execution_plan": {
    "version": "<结构版本号>",
    "root": {
      "node_type": "group",
      "run_mode": "<serial|parallel>",
      "children": [
        {
          "node_type": "<group|intent>"
        }
      ]
    }
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
6. 可以识别多个意图，全部写入 execution_plan.root
7. execution_plan.root 用递归树表达总体顺序、并行关系和嵌套关系
8. 只有在无法稳定判断第一执行步时，才返回 need_clarify=true
9. 输出字段必须严格包含：
primary_intent_code, need_clarify, clarify_question, reason_text, execution_plan
10. execution_plan 必须可被下游直接消费，不允许省略 version、root
11. 如果无法稳定判断第一执行步，则 need_clarify=true，同时 primary_intent_code 为空字符串，execution_plan.root 返回空对象
12. execution_plan.root 没有结果时返回空对象
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

1. 根节点固定使用 `root`
2. `node_type=group`：
   - 表示当前节点只负责编排
   - 用 `run_mode` 定义其子节点关系
   - 用 `children` 承载下一层节点
3. `node_type=intent`：
   - 表示当前节点是可直接执行的叶子意图
4. `run_mode=serial`：
   - 当前 group 内的 `children` 按数组顺序执行
5. `run_mode=parallel`：
   - 当前 group 内的 `children` 可并行执行
6. 无法稳定判断第一执行步时：
   - `need_clarify=true`
   - `root` 输出空对象
7. `primary_intent_code` 通常与根节点下首个主执行 intent 保持一致
8. 每个 `intent` 节点同时保留意图名称、路由目标、协作模式和原因说明
9. 下游按树结构递归消费：遇到 serial 按顺序执行，遇到 parallel 并行执行，遇到 intent 直接路由
10. 如果出现“先 A，再同时处理 B 和 C”这类场景，应输出 serial group，第二个 child 再嵌套 parallel group

推荐示例：

```json
{
  "primary_intent_code": "add_shop_cart",
  "need_clarify": false,
  "clarify_question": "",
  "reason_text": "用户同时表达了加购和下单诉求，当前第一执行步是加购。",
  "execution_plan": {
    "version": "2.0",
    "root": {
      "node_type": "group",
      "run_mode": "serial",
      "children": [
        {
          "node_type": "intent",
          "intent_name_cn": "添加购物车",
          "intent_code": "add_shop_cart",
          "target_agent": "交易Agent",
          "collaboration_mode": "serial",
          "reason_text": "用户明确表达了将商品加入购物车。"
        },
        {
          "node_type": "intent",
          "intent_name_cn": "立即下单",
          "intent_code": "place_order_oow",
          "target_agent": "交易Agent",
          "collaboration_mode": "serial",
          "reason_text": "用户同时表达了后续下单诉求，但执行顺序在加购之后。"
        }
      ]
    }
  }
}
```

嵌套示例：

```json
{
  "primary_intent_code": "view_items",
  "need_clarify": false,
  "clarify_question": "",
  "reason_text": "用户要求先推荐，再并行查看购物车和订单。",
  "execution_plan": {
    "version": "2.0",
    "root": {
      "node_type": "group",
      "run_mode": "serial",
      "children": [
        {
          "node_type": "intent",
          "intent_name_cn": "商品推荐",
          "intent_code": "view_items",
          "target_agent": "商推Agent",
          "collaboration_mode": "single",
          "reason_text": "用户先要求推荐低糖零食。"
        },
        {
          "node_type": "group",
          "run_mode": "parallel",
          "children": [
            {
              "node_type": "intent",
              "intent_name_cn": "查询购物车",
              "intent_code": "view_shop_cart",
              "target_agent": "交易Agent",
              "collaboration_mode": "single",
              "reason_text": "用户要求同时查看购物车。"
            },
            {
              "node_type": "intent",
              "intent_name_cn": "查询订单",
              "intent_code": "query_order",
              "target_agent": "交易Agent",
              "collaboration_mode": "single",
              "reason_text": "用户要求同时查看订单。"
            }
          ]
        }
      ]
    }
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
| 大模型输出主意图编码 | `{{primary_intent_code}}` |
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
- `target_agent`、`collaboration_mode` 等下游执行信息不再单独从顶层读取，应从 `execution_plan.root` 的 intent 节点获取

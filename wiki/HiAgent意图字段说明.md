# HiAgent意图字段说明

本文只用于知识库字段说明，聚焦字段名称、字段类型和字段含义，不展开具体取值、不重复描述 Python 工作流实现。

## 1. 意图配置字段

| 字段名 | 类型 | 含义 |
| --- | --- | --- |
| `intent_name_cn` | string | 意图的中文名称，用于业务阅读、配置排查和结果展示。 |
| `intent_code` | string | 意图的系统编码，是意图在配置、识别和路由中的唯一标识。 |
| `target_agent` | string | 当前意图命中后应路由到的目标智能体。 |
| `collaboration_mode` | string | 当前意图在整体协作链路中的处理模式，用于表达是单独处理还是需要串行协作。 |
| `description` | string | 对该意图业务语义的简要说明，用于帮助理解意图边界。 |
| `examples` | array[string] | 该意图对应的典型用户表达示例，用于辅助理解口语化说法和识别范围。 |
| `priority` | number | 意图优先级字段，用于在多意图场景下辅助判断优先顺序。 |
| `enabled` | boolean | 该意图当前是否参与正式识别和路由。 |
| `default_clarify_question` | string | 当系统无法稳定判断主意图时使用的默认澄清话术。 |

## 2. 意图识别结果字段

| 字段名 | 类型 | 含义 |
| --- | --- | --- |
| `primary_intent_code` | string | 当前轮识别出的主意图编码，表示最优先执行的意图。 |
| `need_clarify` | boolean | 当前输入是否需要继续澄清后才能稳定判断主意图。 |
| `clarify_question` | string | 当需要澄清时返回给用户的问题内容。 |
| `reason_text` | string | 对本轮整体识别结果的简要原因说明。 |
| `execution_plan` | object | 提供给下游执行编排使用的标准化执行计划。 |

## 3. execution_plan 字段

| 字段名 | 类型 | 含义 |
| --- | --- | --- |
| `version` | string | 执行计划结构版本号，用于下游兼容处理。 |
| `root` | object | 执行计划根节点，用递归树方式表达串行、并行和嵌套关系。 |

## 4. execution_plan.root / group 节点子字段

| 字段名 | 类型 | 含义 |
| --- | --- | --- |
| `node_type` | string | 节点类型；用于区分当前节点是编排组节点还是意图叶子节点。 |
| `run_mode` | string | 当前组节点内部子节点的执行方式，用于表达串行或并行。 |
| `children` | array[object] | 当前组节点的子节点列表；子节点既可以是组节点，也可以是意图节点。 |

## 5. execution_plan.root.children 中的 intent 节点子字段

| 字段名 | 类型 | 含义 |
| --- | --- | --- |
| `node_type` | string | 节点类型；用于标识当前节点是一个可直接执行的意图节点。 |
| `intent_name_cn` | string | 该执行步骤对应的意图中文名称。 |
| `intent_code` | string | 该执行步骤对应的意图编码。 |
| `target_agent` | string | 该执行步骤对应的目标智能体。 |
| `collaboration_mode` | string | 该执行步骤对应的协作模式。 |
| `reason_text` | string | 该执行步骤被纳入执行计划的原因说明。 |

## 6. execution_plan 标准规则

| 规则项 | 含义 |
| --- | --- |
| `node_type=group` | 表示当前节点是编排节点，只负责表达子节点之间的执行关系。 |
| `node_type=intent` | 表示当前节点是叶子执行节点，可直接路由到对应目标智能体。 |
| `run_mode=serial` | 表示当前组节点内的 `children` 按数组顺序依次执行。 |
| `run_mode=parallel` | 表示当前组节点内的 `children` 可并行执行。 |
| `children` | 通过节点嵌套表达多层编排；下游按树结构递归消费。 |
| `primary_intent_code` | 表示当前轮主意图编码；通常与根节点下首个主执行意图一致。 |
| `execution_plan.root` | 同时承载识别结果、串行/并行关系、执行顺序和嵌套结构，是下游优先消费的结构化字段。 |
| `need_clarify=true` | 表示当前轮无法稳定生成执行计划，此时 `root` 返回空对象。 |

## 7. 使用边界

- 本文只解释字段含义，不列字段具体值
- 本文不包含 Python 节点接口、工作流节点编排或提示词实现细节

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
| `mode` | string | 当前轮整体执行模式；当前阶段只输出单智能体或串行，无法判断时输出空字符串。 |
| `steps` | array[object] | 下游实际执行步骤列表。 |

## 4. execution_plan.steps 子字段

| 字段名 | 类型 | 含义 |
| --- | --- | --- |
| `step_no` | number | 执行步骤顺序号。 |
| `intent_name_cn` | string | 该执行步骤对应的意图中文名称。 |
| `intent_code` | string | 该执行步骤对应的意图编码。 |
| `target_agent` | string | 该执行步骤对应的目标智能体。 |
| `collaboration_mode` | string | 该执行步骤对应的协作模式。 |
| `reason_text` | string | 该执行步骤被纳入执行计划的原因说明。 |

## 5. execution_plan 标准规则

| 规则项 | 含义 |
| --- | --- |
| `execution_plan.mode=single` | 表示当前轮只需执行一个主步骤，下游可按单智能体直达处理。 |
| `execution_plan.mode=serial` | 表示当前轮存在明确先后顺序，下游应按 `step_no` 依次执行。 |
| `execution_plan.mode=""` | 表示当前轮无法稳定判断第一执行步，需要先向用户澄清。 |
| `steps.step_no` | 用于表达执行顺序；数字越小表示越早执行。 |
| `primary_intent_code` | 应与 `execution_plan.steps` 的首个主执行意图保持一致。 |
| `execution_plan.steps` | 同时承载识别结果与执行顺序，是下游优先消费的结构化字段。 |
| `parallel` | 保留为后续扩展能力，当前阶段不作为首轮标准输出。 |

## 6. 使用边界

- 本文只解释字段含义，不列字段具体值
- 本文不包含 Python 节点接口、工作流节点编排或提示词实现细节

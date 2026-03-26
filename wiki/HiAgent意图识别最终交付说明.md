# HiAgent意图识别最终交付说明

本文用于汇总本次 HiAgent 意图识别方案的全部交付物，并给出推荐使用顺序。

## 1. 交付目标

本次交付只覆盖 HiAgent 平台中的 `意图识别` 能力建设，目标是先完成一条稳定、可调试、可回归的最小识别链路。

不包含：

- 插件接入
- 子智能体调用
- 槽位补全执行
- 业务接口调用

## 2. 最终流程

推荐在平台上按以下流程落地：

```text
Start
  -> Python（intent_mapping_workflow，action=get_enabled_intents）
  -> 大模型（意图识别与结构化输出）
  -> 选择器
     -> need_clarify == false -> End
     -> need_clarify == true -> 消息（澄清） -> End
```

说明：

- `Start` 提供用户输入 `query`
- `Python` 前置节点负责输出 `intents` 和 `default_clarify_question`
- `大模型` 只根据前置节点输出做结构化识别
- `选择器` 负责按 `need_clarify` 分流
- `消息` 仅用于澄清
- `intents_analysis` 当前只做记录，不参与本轮路由

## 3. 交付物清单

### 3.1 完整实现方案

[HiAgent意图映射文档.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图映射文档.md)

用于说明意图映射口径，严格依据 1.3 Agent 与业务中心映射、2.0 意图关键词、2.3 HiAgent 智能体协作关系图。

### 3.2 平台配置字段表

[HiAgent意图识别平台配置字段表.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图识别平台配置字段表.md)

用于直接复制平台录入字段，是唯一配置录入口径，已按“大模型节点 + 系统提示词/用户提示词”口径整理。
当前已更新为“Python 前置节点 + 大模型节点 + 选择器”口径。

### 3.3 测试用例表

[HiAgent意图识别测试用例表.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图识别测试用例表.md)

用于开发调试、联调回归和上线前验收。

## 4. 最终保留文档

为避免后续维护分散，建议长期只维护以下 4 份：

1. [HiAgent意图识别最终交付说明.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图识别最终交付说明.md)
2. [HiAgent意图映射文档.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图映射文档.md)
3. [HiAgent意图识别测试用例表.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图识别测试用例表.md)
4. [HiAgent意图识别平台配置字段表.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图识别平台配置字段表.md)

职责如下：

- `最终交付说明`：负责范围、流程、使用顺序
- `意图映射文档`：负责正式意图名、目标智能体和协作模式口径
- `平台配置字段表`：负责平台实际录入内容
- `测试用例表`：负责调试与回归标准

## 5. 文档维护原则

后续变更建议按下面原则维护：

1. 意图定义、目标智能体和协作模式变化，优先修改 `意图映射文档`
2. 平台节点配置变化，优先修改 `平台配置字段表`
3. 测试口径变化，优先修改 `测试用例表`
4. 流程边界或交付范围变化，优先修改 `最终交付说明`

## 6. 推荐使用顺序

建议按以下顺序使用：

1. 先看 `最终交付说明`
2. 再看 `意图映射文档`
3. 按 `平台配置字段表` 在平台录入
4. 用 `测试用例表` 做调试和回归

## 7. 实际落地顺序

平台落地建议按下面执行：

1. 创建 `对话流型 Beta` 智能体
2. 配置 Python 前置节点 `intent_mapping_workflow`
3. 按平台配置字段表录入大模型提示词和选择器条件
4. 跑测试用例
5. 调优提示词边界规则并回归

## 8. 验收口径

验收时重点看：

- Python 前置节点输出的 `intents` 是否完整
- 高频样例识别是否稳定
- 边界样例是否明显误判
- 多意图输入是否能稳定输出主意图，`intents_analysis` 是否合理
- 模糊输入是否优先落到 `need_clarify=true`
- `reason_text` 是否有解释价值

建议目标：

- 主意图识别准确率 >= 90%
- 模糊输入兜底稳定
- 边界样例误判率可控

## 9. 后续迭代建议

只有当意图识别稳定后，再进入下一阶段：

1. 增加槽位提取
2. 增加更细路由分支
3. 接入插件或 HTTP 请求
4. 再考虑子智能体分发

不要跳过“识别稳定”直接进入业务执行链路。

## 10. 上线执行清单

### 10.1 配置清单

上线前逐项确认：

1. 已创建 `对话流型 Beta` 智能体
2. 已接入 Python 前置节点 `intent_mapping_workflow`
3. Python 节点入参固定为：

```json
{
  "action": "get_enabled_intents"
}
```

4. 大模型节点已使用最新版系统提示词
5. 大模型节点已使用最新版用户提示词
6. 大模型节点已显式映射输出字段：

```text
intent_name_cn
intent_code
target_agent
collaboration_mode
need_clarify
clarify_question
reason_text
primary_intent_code
intents_analysis
```

7. 选择器只按 `need_clarify` 分流
8. `intents_analysis` 当前只记录，不参与本轮路由

### 10.2 联调清单

联调时逐项确认：

1. Python 前置节点能稳定返回 `intents`
2. 大模型节点能稳定输出合法 JSON
3. 输出的 `intent_code` 必须存在于 `intents`
4. 输出的 `target_agent`、`collaboration_mode` 必须与前置配置一致
5. 模糊输入能正确走 `need_clarify=true`
6. 多意图输入能输出一个主意图和合理的 `intents_analysis`

### 10.3 回归清单

上线前至少回归以下样例：

- TC001
- TC005
- TC010
- TC014
- TC019
- TC022
- TC026
- TC027
- TC030

### 10.4 验收清单

验收通过标准：

- 主意图识别准确率 >= 90%
- 高频场景识别稳定
- 模糊输入优先澄清
- 多意图输入主次关系基本正确
- 无明显越权输出，不能出现 `intents` 之外的 `intent_code`
- 无明显格式错误，输出 JSON 可被平台稳定解析

### 10.5 上线后观察项

上线后重点观察：

1. 高频误判 Top case
2. 澄清触发率是否过高
3. 多意图输入中 `intents_analysis` 是否稳定
4. 是否出现未定义 `intent_code`
5. 是否出现主意图和 `target_agent` 不一致

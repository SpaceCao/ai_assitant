# CLAUDE.md

This repository is a reduced HiAgent intent-mapping workspace for the Laiyifen shopping assistant.

## Scope

- Source-of-truth config: `python/intent_mapping_workflow.py`
- HiAgent import/export file: `config/intents.csv`
- Main wiki index: `manifest.json`
- Maintained wiki docs:
  - `wiki/HiAgent意图映射文档.md`
  - `wiki/HiAgent意图识别平台配置字段表.md`
  - `wiki/HiAgent意图识别测试用例表.md`
  - `wiki/HiAgent意图识别最终交付说明.md`

## Mapping Rules

Intent definitions must align with:

1. `1.3 Agent 与业务中心映射`
2. `2.0 意图关键词`
3. `2.3 HiAgent 智能体协作关系图`

Current formal intent codes are:

- `view_items`
- `view_shop_cart`
- `add_shop_cart`
- `del_shop_cart`
- `clear_shop_cart`
- `confirm_order`
- `place_order_oow`
- `cancel_order`
- `query_order`
- `knowledge_quiz`
- `casual_reply`

Do not reintroduce older custom intent-code schemes unless explicitly requested.

## Workflow

When changing mappings:

1. Update `python/intent_mapping_workflow.py`
2. Update `config/intents.csv` if platform-facing data changed
3. Update `wiki/HiAgent意图映射文档.md` if the formal mapping changed
4. Check `wiki/HiAgent意图识别测试用例表.md` for affected cases

## Validation

Use:

```bash
python3 python/test_intent_mapping_workflow.py
python3 -m py_compile python/intent_mapping_workflow.py python/test_intent_mapping_workflow.py
python3 -m json.tool manifest.json
```

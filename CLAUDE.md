# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A configuration and documentation workspace for the Laiyifen (来伊份) AI shopping assistant's intent recognition layer, built on the ByteDance HiAgent platform. There is no running application here — this repo defines how user intents are recognized and routed to specialized agents.

## Architecture

The intent recognition flow on HiAgent:

1. Pre-processing node calls `handler()` from `python/intent_mapping_workflow.py` → returns enabled intents + default clarification question
2. LLM node (Doubao-1.5-pro-32k) performs structured intent recognition against that list
3. Selector node branches on `need_clarify`: routes to target agent or outputs clarification

Six agents in the system:
- Intent Agent (意图Agent) — orchestrator, recognition + dispatch
- Product Recommendation Agent (商推Agent) — product/scene recommendations (`view_items`)
- Transaction Agent (交易Agent) — cart + orders (`view_shop_cart`, `add_shop_cart`, `del_shop_cart`, `clear_shop_cart`, `confirm_order`, `place_order_oow`, `cancel_order`, `query_order`)
- Q&A Agent (问答Agent) — FAQ, product knowledge (`knowledge_quiz`)
- User Agent (用户Agent) — user profiles (no intent currently routed)
- Chat Agent (闲聊Agent) — casual fallback (`casual_reply`)

## Key Files

- `python/intent_mapping_workflow.py` — source-of-truth config. Exports `handler(params)` with 4 actions: `get_enabled_intents` (default), `get_all_intents`, `get_intent_by_code`, `get_mapping_rules`
- `python/test_intent_mapping_workflow.py` — local test script (must run from `python/` dir or adjust sys.path)
- `config/intents.csv` — platform-facing intent export (11 intents)
- `manifest.json` — wiki index + decision tree
- `wiki/HiAgent意图映射文档.md` — comprehensive mapping doc with workflow templates (T01–T06)
- `wiki/HiAgent意图识别平台配置字段表.md` — exact LLM prompts, selector conditions, output fields
- `wiki/HiAgent意图识别测试用例表.md` — 33 test cases (regression, boundary, multi-intent, fuzzy)
- `wiki/HiAgent意图识别最终交付说明.md` — delivery scope and go-live checklists
- `wiki/HiAgent意图字段说明.md` — field reference (not tracked in manifest.json)

## Formal Intent Codes

`view_items`, `view_shop_cart`, `add_shop_cart`, `del_shop_cart`, `clear_shop_cart`, `confirm_order`, `place_order_oow`, `cancel_order`, `query_order`, `knowledge_quiz`, `casual_reply`

Do not reintroduce older custom intent-code schemes unless explicitly requested.

## Mapping Rules

Intent definitions must align with these architecture document sections:
1. `1.3 Agent 与业务中心映射`
2. `2.0 意图关键词`
3. `2.3 HiAgent 智能体协作关系图`

## Change Workflow

When changing mappings:
1. Update `python/intent_mapping_workflow.py`
2. Update `config/intents.csv` if platform-facing data changed
3. Update `wiki/HiAgent意图映射文档.md` if the formal mapping changed
4. Check `wiki/HiAgent意图识别测试用例表.md` for affected cases

## Validation

```bash
python3 python/test_intent_mapping_workflow.py
python3 -m py_compile python/intent_mapping_workflow.py python/test_intent_mapping_workflow.py
python3 -m json.tool manifest.json
```

## Conventions

- JSON: 2-space indentation, double-quoted keys
- Markdown: concise, task-oriented headings
- Commits: short imperative, e.g. `docs: align mapping with architecture pdf`, `config: update intent route targets`
- PRs: state which architecture/PRD section changed, list affected intent codes, note test cases to rerun

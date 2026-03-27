# Repository Guidelines

## Project Structure & Module Organization
This repository is now a focused HiAgent intent-mapping workspace. Core files are `python/intent_mapping_workflow.py` as the runtime source-of-truth configuration, `config/intents.csv` as the platform-friendly export, and `manifest.json` as the wiki index. Main documentation lives in `wiki/` and is intentionally reduced to `Home.md` plus five maintained documents for mapping, platform configuration, field knowledge, testing, and final delivery.

## Build, Test, and Development Commands
There is no build step. Use lightweight validation before changing configs or docs:

```bash
python3 python/test_intent_mapping_workflow.py
python3 -m py_compile python/intent_mapping_workflow.py python/test_intent_mapping_workflow.py
rg --files wiki config python
```

These commands validate the workflow interface and confirm expected file layout.

## Coding Style & Naming Conventions
Write Markdown concisely and keep headings task-oriented. In JSON, use two-space indentation and double-quoted keys. Intent definitions must follow the architecture-document naming, for example `view_items`, `view_shop_cart`, `knowledge_quiz`, and `casual_reply`. Do not introduce alternate intent-code schemes without first updating the mapping document.

## Testing Guidelines
Use [HiAgent意图识别测试用例表.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图识别测试用例表.md) as the regression source. When intent mappings change, update both [intent_mapping_workflow.py](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/python/intent_mapping_workflow.py) and [HiAgent意图映射文档.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图映射文档.md), then rerun the affected cases.

## Commit & Pull Request Guidelines
Use short imperative commits such as `docs: align mapping with architecture pdf` or `config: update intent route targets`. In pull requests, state which architecture or PRD section changed, list affected intent codes, and note any test cases that must be rerun.

## Contributor Notes
Treat [HiAgent意图映射文档.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图映射文档.md), [HiAgent意图识别平台配置字段表.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图识别平台配置字段表.md), [HiAgent意图字段说明.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图字段说明.md), [HiAgent意图识别测试用例表.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图识别测试用例表.md), and [HiAgent意图识别最终交付说明.md](/Users/caoxingming/laiyifen-codes/ai_agent/laiyifen-ai/ai_assitant/wiki/HiAgent意图识别最终交付说明.md) as the only maintained wiki pages.

# 測試說明

這個資料夾為 pipeline 中**可離線測試的純邏輯模組**提供 pytest 單元測試。
重量級/會連網路的相依（`tensorflow`、`transformers`、`SPARQLWrapper`、DBpedia endpoint）
不需要安裝——`conftest.py` 會：

1. 把 repo root 加進 `sys.path`（本專案是以 repo root 為基準的相對 import）。
2. 對 `SPARQLWrapper` 與 `nltk` 塞入輕量 stub，讓 `AnswerTypeExtractor` 能被載入，
   同時保證測試若不慎踩到會發網路請求的分支就直接失敗（而不是真的連線）。

## 執行方式

```bash
pip install pytest        # 唯一額外相依
python -m pytest tests/ -q # 從 repo root 執行
```

## 覆蓋範圍

| 測試檔 | 受測模組 | 重點 |
|--------|----------|------|
| `test_caculate_entity_tag.py` | `CaculateEntityTag.combineEntity_Tag` | 單/空 token、合併與分段、`sum(counts)==token 數` 的對齊不變量、未知 tag 會 KeyError |
| `test_word_and_entityfinder.py` | `Word`、`EntityFinder` | 存取器、RR 特判、組合標記逐字元展開、未知角色被忽略 |
| `test_answer_type_extractor.py` | `AnswerTypeExtractor` | 疑問詞→答案型別、`extractent` 正規化、Thing/Boolean/Date/Number(無 URI) 的 `filterAnswer` 分支 |

## 以測試釘住的已知缺陷

- `test_number_of_phrase_is_shadowed_by_thing_branch`：`answerTypeExtracting` 裡
  `'number of' in sent` 的判斷被前面 which/what/… 的 Thing 分支遮蔽，
  導致「What is the number of …」類計數問句被誤判為 Thing。詳見 `CODE_REVIEW.md`。

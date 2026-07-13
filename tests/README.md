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

## 迴歸測試（釘住已修正的缺陷）

這些測試對應 `CODE_REVIEW.md` 所列並已修正的缺陷，防止回歸：

- `test_number_of_phrase_triggers_number_even_with_thing_question_word`：#1
  `answerTypeExtracting` 的 `'number of'` 計數判斷被 Thing 分支遮蔽（已提前修正）。
- `test_unknown_tag_is_treated_as_non_entity`：#3 `combineEntity_Tag` 遇未知 tag
  不再 KeyError，改當作 `N`。
- `test_tag_acc_does_not_mutate_predict_input`：#5 `tag_acc` 不再就地修改傳入的 list。
- `test_word_set_entity_url_dedupes_by_membership`：#6 `Word.__setEntityURL__` 去重
  改用 list 成員判斷。

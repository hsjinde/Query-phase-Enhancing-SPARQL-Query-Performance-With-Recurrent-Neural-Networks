# 程式碼審查（Code Review）

範圍：pipeline 中的純邏輯模組（`AnswerTypeExtractor`、`CaculateEntityTag`、
`DBpediaQueries`、`Preprocessor`、`Word`）。以「正確性 > 健壯性 > 可維護性」排序。
可離線驗證的行為已用 `tests/` 下的 pytest 測試釘住。

> **狀態：以下 #1–#6 皆已於本分支修正,並補上對應迴歸測試（共 44 個測試全綠）。**
> 下方保留每項的成因與修正說明,方便審查對照。

---

## 正確性缺陷（Correctness）

### 1. `AnswerTypeExtractor.answerTypeExtracting`：`'number of'` 啟發式被 Thing 分支遮蔽
`AnswerTypeExtractor.py:28-30`

```python
if varible.lower()=='which' or ... or varible.lower() == 'name':
    self.answerType='Thing'
elif ... or 'number of' in sent.lower():
    self.answerType='Number'
```

`'number of' in sent` 放在 `elif`，只要疑問詞是 `which/what/give/show/list/find/name`
其中之一，就會先命中 Thing 分支，`elif` 永遠不會被評估。結果像
**「What is the number of children of X?」** 這類計數問句會被判成 `Thing` 而非 `Number`，
進而套用錯誤的答案篩選邏輯。

- **修正**：把 Number（含 `'number of' in sent`）的判斷「提前」到 Thing 分支之前。
- 迴歸測試：`test_number_of_phrase_triggers_number_even_with_thing_question_word`、
  `test_plain_thing_question_word_without_number_of_stays_thing`。

### 2. `DBpediaQueries.classExtracting`：迭代 list 的同時 `.clear()`，同義詞結果被丟棄
`DBpediaQueries.py:676-681`

```python
for url in LocalDbrMatcher.getMatchedUrl():
    classurl += "<" + url + ">@"
    classExtracting_classSet[nn] = classurl
    LocalDbrMatcher.getMatchedUrl().clear()   # ← 在迭代同一個 list 時清空它
    classurl = ""
```

`getMatchedUrl()` 回傳的是那個 class 層級的**真實 list**，在 `for` 迴圈內對它
`.clear()` 會讓迭代在處理完**第一個** URL 後立即停止——後續同義詞/衍生詞比對到的
class URI 全部被靜默丟棄。對照上方 `DBpediaQueries.py:652-657` 的 `if` 分支才是正確寫法
（迴圈內只累加，迴圈**外**才 clear 一次）。

- **修正**：比照 `if` 分支，把 `.clear()` 與 `classurl = ""` 移到 `for` 迴圈之外。
  （此路徑需連 DBpedia，未加自動化測試，以人工對照修正。）

---

## 健壯性（Robustness）

### 3. `CaculateEntityTag.combineEntity_Tag`：未知 tag 直接 `KeyError`
`CaculateEntityTag.py:6-18`

`tag_dic` 中，組合標記 `CR/CE/ER/VR/RR/L` 只有 `-B`/`-I`，沒有 `-E`。一旦 tagger 偶發吐出
`ER-E`、`O` 之類不在字典裡的標記，`tag_dic[word_tag[i]]` 會 `KeyError` 中斷整條 pipeline。

- **修正**：改用 `tag_dic.get(tag, tag_dic['N'])`，把未知標記當作 `N` 處理。
- 迴歸測試：`test_unknown_tag_is_treated_as_non_entity`。

### 4. `Preprocessor.__init__`：空字串問句會 `IndexError`
`Preprocessor.py:20-21`

```python
sent = sentence.strip()
if sent[-1] in string.punctuation:   # sent 為空時 sent[-1] → IndexError
```

- **修正**：改為 `if sent and sent[-1] in string.punctuation:`。

---

## 可維護性 / 小問題（Maintainability）

### 5. `CaculateEntityTag.tag_acc`：就地修改呼叫端傳入的 `predict`
`CaculateEntityTag.py:66-69` 在長度不足時對 `predict` `append('N')`，屬於對輸入參數的
副作用（side effect），重複評分或共用同一 list 時容易踩雷。

- **修正**：函式開頭先 `predict = list(predict)` 複製再補齊。
- 迴歸測試：`test_tag_acc_does_not_mutate_predict_input`。

### 6. `Word.__setEntityURL__`：去重邏輯脆弱
`Word.py:24-27` 用 `if url not in str(self.__entityUrl)` 以「字串子字串」判斷去重——
某個 URL 若是既有 URL 的子字串會被誤判為重複而漏加（此 setter 目前尚未被 pipeline 呼叫，
屬潛在缺陷）。

- **修正**：改成 `url not in self.__entityUrl`（list 成員判斷）。
- 迴歸測試：`test_word_set_entity_url_dedupes_by_membership`。

### 7. 大量中文 `print` 混雜於邏輯中（未處理）
多數模組把除錯輸出直接 `print`，不利於當函式庫重用與測試時的雜訊控制。
建議長期改用 `logging` 並分級，短期至少集中在入口層。此項屬風格改動，本次未動。

---

## 測試

新增 `tests/`（pytest，唯一額外相依為 `pytest`；重量級套件由 `conftest.py` stub 掉，
完全離線）。執行：`python -m pytest tests/ -q`。目前 **44 個測試全綠**，涵蓋上述已修正
缺陷的迴歸測試（#1、#3、#5、#6 各有對應測試；#2 需連 DBpedia、以人工對照修正）。

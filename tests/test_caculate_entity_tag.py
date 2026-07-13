"""`CaculateEntityTag.combineEntity_Tag` 的單元測試。

這個函式是 tagging 與 SPARQL 生成之間的關鍵接縫：它把逐 token 的 BIO 標記
（V-B / R-I / ...）合併成「以 / 分隔的實體字串」以及「每個實體佔幾個 token」的
word-count 陣列。Preprocessor 直接拿這個 count 陣列去切原始句子的 token，
所以 count 的正確性攸關整條 pipeline 是否對齊。
"""
import pytest

from CaculateEntityTag import combineEntity_Tag, tag_acc


def test_single_token_returns_that_tag_and_count_one():
    # 迴歸測試：單一 token 的句子不會進入成對 while 迴圈，
    # 必須被特別處理成 (tag, [1])，否則下游會拿到空字串而斷詞錯誤。
    tag, counts = combineEntity_Tag(["V-B"])
    assert tag == "V-B"
    assert counts == [1]


def test_empty_input_returns_empty():
    tag, counts = combineEntity_Tag([])
    assert tag == ""
    assert counts == []


def test_consecutive_same_entity_is_merged():
    # V-B V-I 屬於同一個實體（編碼相差 1），要被空白合併成一段。
    tag, counts = combineEntity_Tag(["V-B", "V-I"])
    assert tag == "V-B V-I"
    assert counts == [2]


def test_different_entities_are_split_with_slash():
    # V-B 之後接 E-B 是不同實體，中間用 / 分隔，count 陣列各自為 1。
    tag, counts = combineEntity_Tag(["V-B", "E-B"])
    assert tag == "V-B/E-B"
    assert counts == [1, 1]


def test_mixed_sentence_alignment():
    tags = ["V-B", "E-B", "R-B", "R-I"]
    tag, counts = combineEntity_Tag(tags)
    assert tag == "V-B/E-B/R-B R-I"
    assert counts == [1, 1, 2]


@pytest.mark.parametrize(
    "tags",
    [
        ["V-B"],
        ["V-B", "V-I"],
        ["V-B", "E-B"],
        ["V-B", "E-B", "R-B", "R-I"],
        ["V-B", "V-I", "R-B", "N", "E-B", "N", "N", "E-B", "N"],
        ["V-B", "N", "N", "C-B", "R-I", "R-E", "E-B", "N"],
    ],
)
def test_word_counts_sum_to_token_length(tags):
    # 關鍵不變量：count 陣列的總和必須等於 token 數量，
    # 否則 Preprocessor 依 count 切句時會漏字或錯位。
    _, counts = combineEntity_Tag(tags)
    assert sum(counts) == len(tags)


def test_number_of_segments_matches_slash_count():
    tag, counts = combineEntity_Tag(
        ["V-B", "V-I", "R-B", "N", "E-B", "N", "N", "E-B", "N"]
    )
    # 「/ 分隔的段數」應與 count 陣列長度一致（每段一個 count）。
    assert len(tag.split("/")) == len(counts)


def test_unknown_tag_is_treated_as_non_entity():
    # 迴歸測試：修正後，tag_dic 沒有的標記（例如組合標記的 -E 變體 'ER-E'，
    # 字典裡只有 ER-B / ER-I）會被當成非實體 'N'，不再 KeyError 中斷 pipeline。
    tag, counts = combineEntity_Tag(["V-B", "ER-E"])
    assert tag == "V-B/N"
    assert counts == [1, 1]
    assert sum(counts) == 2


def test_tag_acc_does_not_mutate_predict_input():
    # 迴歸測試：predict 比 y 短時，tag_acc 需在內部複製後補齊，
    # 不可就地修改呼叫端傳入的 list。
    predict = ["V-B"]
    y = ["V-B", "E-B"]
    before = list(predict)
    tag_acc(predict, y)
    assert predict == before

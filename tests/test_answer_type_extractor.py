"""`AnswerTypeExtractor` 純邏輯部分的單元測試。

只測不會發出網路請求的部分：
  - answerTypeExtracting：依問句的疑問詞判斷期望答案型別
  - extractent：把 URI / XMLSchema 型別字串正規化
  - filterAnswer：Thing / Boolean / Date / Number(無 URI) 這幾條不連網路的分支
Person or Organization / Place / Number(URI) 分支會呼叫 executeSparql（連 DBpedia），
在 conftest 的 stub 下會直接 assert 失敗，因此本檔刻意避開那些分支。
"""
import pytest

from AnswerTypeExtractor import AnswerTypeExtractor


@pytest.fixture
def at():
    return AnswerTypeExtractor()


# --- answerTypeExtracting -----------------------------------------------------
@pytest.mark.parametrize(
    "vary, expected",
    [
        (["is"], "Boolean"),
        (["Are"], "Boolean"),        # 大小寫不敏感
        (["was"], "Boolean"),
        (["which"], "Thing"),
        (["List"], "Thing"),
        (["who"], "Person or Organization"),
        (["whose"], "Person or Organization"),
        (["where"], "Place"),
        (["when"], "Date"),
        (["how many"], "Number"),
        (["count"], "Number"),
        (["banana"], "Thing"),        # 未知疑問詞 fallback 到 Thing
    ],
)
def test_answer_type_from_question_word(at, vary, expected):
    assert at.answerTypeExtracting(vary, "irrelevant sentence") == expected


def test_empty_variable_list_falls_back_to_thing(at):
    # V 清單為空（例如標記失敗）時，取 varible[0] 會丟例外並被吃掉成 ''，
    # 最終落到 Thing。這裡把該防呆行為釘住。
    assert at.answerTypeExtracting([], "some question") == "Thing"


def test_number_of_phrase_triggers_number_even_with_thing_question_word(at):
    # 迴歸測試：修正後 'number of' 的計數判斷排在 Thing 之前，
    # 「What is the number of ...」這種計數問句即使疑問詞是 what 也會正確判為 Number。
    assert at.answerTypeExtracting(["what"], "the number of moons") == "Number"


def test_number_of_phrase_triggers_number_for_unrecognised_question_word(at):
    assert at.answerTypeExtracting(["banana"], "the number of moons") == "Number"


def test_plain_thing_question_word_without_number_of_stays_thing(at):
    # 沒有 'number of' 線索時，which/what 仍應維持 Thing，確認重排沒有誤傷一般問句。
    assert at.answerTypeExtracting(["what"], "the capital of France") == "Thing"


# --- extractent ---------------------------------------------------------------
@pytest.mark.parametrize(
    "raw, expected_is_entity, expected_value",
    [
        ("http://dbpedia.org/resource/Berlin", True, "Berlin"),
        ("plain text answer", False, "plain text answer"),
    ],
)
def test_extractent(at, raw, expected_is_entity, expected_value):
    is_ent, value = at.extractent(raw)
    assert is_ent is expected_is_entity
    assert value == expected_value


# --- filterAnswer：不連網路的分支 --------------------------------------------
def test_filter_answer_boolean_true_when_answers_exist(at):
    at.answerTypeExtracting(["is"], "Is Berlin a city")
    assert at.filterAnswer(["something"]) == ["True"]


def test_filter_answer_boolean_false_when_no_answers(at):
    at.answerTypeExtracting(["is"], "Is Berlin a city")
    # 全空答案 → Boolean False。注意 filterAnswer 尾端有
    # 「if tmpAns == []: tmpAns = ans」的保底，但 Boolean 分支一定會塞入 'False'，
    # 所以不受影響。
    assert at.filterAnswer([""]) == ["False"]


def test_filter_answer_date_keeps_only_date_typed(at):
    at.answerTypeExtracting(["when"], "When was it founded")
    answers = [
        "1990-01-01^^http://www.w3.org/2001/XMLSchema#date",
        "http://dbpedia.org/resource/SomeThing",
    ]
    result = at.filterAnswer(answers)
    assert result == ["1990-01-01^^http://www.w3.org/2001/XMLSchema#date"]


def test_filter_answer_number_without_schema_counts_answers(at):
    at.answerTypeExtracting(["how many"], "How many moons")
    # 答案裡沒有 XMLSchema/xsd → 回傳答案「數量」的字串。
    result = at.filterAnswer(["a", "b", "c"])
    assert result == ["3"]


def test_filter_answer_thing_passes_through_unique(at):
    at.answerTypeExtracting(["which"], "Which cities")
    result = at.filterAnswer(["Berlin", "Berlin", "Paris"])
    assert sorted(result) == ["Berlin", "Paris"]


def test_filter_answer_empty_input_returns_empty(at):
    # ans 為空 → found_answer 為空 → 各型別分支多半得到空 tmpAns，
    # 最後保底 tmpAns = ans（仍為空）。確認不會爆例外。
    at.answerTypeExtracting(["which"], "Which cities")
    assert at.filterAnswer([]) == []

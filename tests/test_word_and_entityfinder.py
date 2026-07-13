"""`Word` 與 `EntityFinder` 的單元測試。

EntityFinder 負責把已標記的 Word 依 ERC 角色分流到 V/E/R/RR/C 五個清單，
是 URI 解析與 SPARQL 生成的輸入來源。
"""
from Word import Word
from EntityFinder import EntityFinder


def test_word_basic_accessors():
    w = Word("Berlin", "berlin", "NNP", "E")
    assert w.getWord() == "Berlin"
    assert w.getLemma() == "berlin"
    assert w.getPos() == "NNP"
    assert w.getERC() == "E"
    # __setEntityURL__ 未被呼叫時，getEntityURL 預期為空 list。
    assert w.getEntityURL() == []


def test_word_set_entity_url_dedupes_by_membership():
    # 迴歸測試：去重應以 list 成員判斷，而非對 list 字串表示做子字串比對。
    # 「是既有 URL 子字串」的 URL 不應被誤判為重複而漏加。
    w = Word("Berlin", "berlin", "NNP", "E")
    # __setEntityURL__ 有雙尾底線，不觸發名稱修飾，可直接呼叫。
    w.__setEntityURL__(["http://dbpedia.org/resource/Berlin"])
    w.__setEntityURL__(["http://dbpedia.org/resource/Berlin"])  # 重複 → 不再加入
    w.__setEntityURL__(["http://dbpedia.org/resource/Berlin_Wall"])  # 子字串包含既有 URL → 仍須加入
    assert w.getEntityURL() == [
        "http://dbpedia.org/resource/Berlin",
        "http://dbpedia.org/resource/Berlin_Wall",
    ]


def test_entityfinder_routes_single_roles():
    words = [
        Word("what", "what", "WP", "V"),
        Word("Berlin", "berlin", "NNP", "E"),
        Word("capital", "capital", "NN", "C"),
        Word("located", "locate", "VBN", "R"),
    ]
    ef = EntityFinder(words)
    assert ef.getV() == ["what"]
    assert ef.getE() == ["Berlin"]
    assert ef.getC() == ["capital"]
    assert ef.getR() == ["located"]
    assert ef.getRR() == []


def test_entityfinder_rr_is_special_cased():
    # 'RR' 是被整段特判的角色，不會被逐字元拆解成兩個 'R'。
    words = [Word("famous", "famous", "JJ", "RR")]
    ef = EntityFinder(words)
    assert ef.getRR() == ["famous"]
    assert ef.getR() == []


def test_entityfinder_combined_tag_is_split_per_char():
    # 組合標記（例如 'ER'）會被逐字元展開，同時進入 E 與 R 兩個清單。
    words = [Word("director", "director", "NN", "ER")]
    ef = EntityFinder(words)
    assert ef.getE() == ["director"]
    assert ef.getR() == ["director"]


def test_entityfinder_ignores_unknown_role_chars():
    # 'N'（非實體）等未知角色字元不屬於 V/E/R/C，應被忽略、不進任何清單。
    words = [Word("the", "the", "DT", "N")]
    ef = EntityFinder(words)
    assert ef.getV() == []
    assert ef.getE() == []
    assert ef.getR() == []
    assert ef.getC() == []
    assert ef.getRR() == []

"""pytest 共用設定。

這個 codebase 沒有安裝套件、沒有 __init__.py，import 是以 repo root 為基準的相對名稱
（例如 `from Word import Word`）。因此測試前必須把 repo root 加進 sys.path。

另外，`AnswerTypeExtractor` 在 module 載入時就會 import `SPARQLWrapper` 與 `nltk`，
而這兩個重量級套件在純單元測試環境不一定安裝，也不該為了測純函式而連上 DBpedia。
我們在這裡塞入極輕量的假模組（stub），讓純邏輯（答案型別判斷、字串去重）可以離線被測。
只要測試不去踩到真的會發網路請求的分支（Person/Place/Number-URI），這些 stub 就足夠。
"""
import os
import sys
import types

# --- 讓 repo root 上的模組可以被 import ---------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


# --- 針對重量級/會連網路的相依提供 stub --------------------------------------
def _install_sparqlwrapper_stub():
    if "SPARQLWrapper" in sys.modules:
        return
    mod = types.ModuleType("SPARQLWrapper")

    class _FakeSPARQL:
        """假的 SPARQLWrapper：任何實際查詢都會爆炸，確保測試不會誤打 DBpedia。"""

        def __init__(self, *a, **k):
            pass

        def setQuery(self, *a, **k):
            pass

        def setReturnFormat(self, *a, **k):
            pass

        def query(self, *a, **k):
            raise AssertionError(
                "測試不應該真的發出 SPARQL 查詢；請避開會連網路的答案型別分支"
            )

    mod.SPARQLWrapper = _FakeSPARQL
    mod.JSON = "json"
    sys.modules["SPARQLWrapper"] = mod


def _install_nltk_stub():
    if "nltk" in sys.modules:
        return
    mod = types.ModuleType("nltk")

    def _word_tokenize(s):
        return s.split()

    def _pos_tag(tokens):
        return [(t, "NN") for t in tokens]

    mod.word_tokenize = _word_tokenize
    mod.pos_tag = _pos_tag

    stem = types.ModuleType("nltk.stem")

    class _FakeLemmatizer:
        def lemmatize(self, word, pos="n"):
            return word

    stem.WordNetLemmatizer = _FakeLemmatizer
    mod.stem = stem
    sys.modules["nltk"] = mod
    sys.modules["nltk.stem"] = stem


_install_sparqlwrapper_stub()
_install_nltk_stub()

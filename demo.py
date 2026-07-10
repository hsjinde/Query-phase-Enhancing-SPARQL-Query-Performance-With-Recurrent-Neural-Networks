# -*- coding: utf-8 -*-
"""
End-to-end demo: 對幾個自然語言問句跑完整 KGQA pipeline,
從語義角色標註 → 實體/屬性連結 → SPARQL 生成 → 對 live DBpedia 查詢 → 答案。

用法 (需先備妥 model/、data/、SQLite/ 等資產,見 README):
    python demo.py

需要網路連線至 http://dbpedia.org/sparql。
"""
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"       # 強制 CPU
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"        # 收斂 TF log

# 讓 Windows 終端機也能正確顯示中文輸出
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import joblib
from Preprocessor import Preprocessor
from Preprocessor_Bert import LCQUAD
from DBpediaQueries import DBpediaQueries
from EntityFinder import EntityFinder
from AnswerTypeExtractor import AnswerTypeExtractor
from SPARQLgeneration import SPARQLgeneration
from ERC_Tagger import ERC_Tagger

# 分類器輸出的整數 → 模板代碼 (見 README 的 template code 說明)
DICTIONARY = ['A', 'AA', 'AAB', 'AB', 'AC', 'B', 'BB', 'BBB', 'BBC', 'BBc',
              'BbC', 'Bbb', 'Bbc', 'D', 'aBC', 'aC', 'abc', 'ac', 'bC', 'bbc', 'bc']

QUESTIONS = [
    "What is the capital of Japan?",
    "Who is the wife of Barack Obama?",
]


def answer_question(question, ERC, classifiers, svm):
    print("\n" + "=" * 70)
    print("問句:", question)

    # 1) 模板分類 (14 個 BERT 二元分類器 → 特徵向量 → SVM)
    feats = LCQUAD.predict(classifiers, LCQUAD.tokenize(question))
    template = DICTIONARY[svm.predict(feats)[0]]
    print("模板:", template)

    # 2) ERC 語義角色標註 + 角色抽取
    q = question[:-1] if question[-1] in "?." else question
    parsed = Preprocessor(q, ERC).getParsingResult()
    EF = EntityFinder(parsed)
    E, R, C, RR = EF.getE(), EF.getR(), EF.getC(), EF.getRR()

    # 3) URI 解析 (DBpedia + 本地 SQLite 字典)
    dbq = DBpediaQueries()
    NamedEntity = dbq.NamedEntityExtracting(EF.E, parsed)
    Class = dbq.classExtracting(EF.C, parsed)
    Property = dbq.propertyExtracting(EF.R, parsed)
    print("實體:", NamedEntity, "| 屬性:", list(Property.keys()), "| 類別:", Class)

    # 4) SPARQL 生成 + 對 DBpedia 執行
    dbq.clearResult()
    answer, _, _ = SPARQLgeneration().SPARQLgeneration(
        NamedEntity, Property, Class, E, R, RR, C, template)
    answer = list(set(answer))

    # 5) 答案型別過濾
    at = AnswerTypeExtractor()
    at.answerTypeExtracting(EF.getV(), q)
    final = at.filterAnswer(answer) if answer else []
    print("答案型別:", at.getAnswerType())
    print(">>> 答案:", final[:10])


def main():
    print(">>> 載入 ERC 標註器 (GloVe + BiLSTM-CRF) ...")
    ERC = ERC_Tagger(use_bert=False)
    print(">>> 載入 14 個 BERT 模板分類器 (首次會下載 bert-base-cased) ...")
    classifiers = LCQUAD.classifiers()
    print(">>> 載入 SVM ...")
    svm = joblib.load("./model/LCQUAD/svm_LCQUAD")

    for question in QUESTIONS:
        answer_question(question, ERC, classifiers, svm)


if __name__ == "__main__":
    main()

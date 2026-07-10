import os
import sys
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 讓 Windows 終端機也能正確顯示中文
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

dictionary = ['A', 'AA', 'AAB', 'AB', 'AC', 'B', 'BB', 'BBB', 'BBC', 'BBc',
              'BbC', 'Bbb', 'Bbc', 'D', 'aBC', 'aC', 'abc', 'ac', 'bC', 'bbc', 'bc']


class QA_withDBpedia():
    def main(self):
        ERC = ERC_Tagger(use_bert=False)
        classifiers = LCQUAD.classifiers()
        loaded_model = joblib.load('./model/LCQUAD/svm_LCQUAD')

        print("\n準備完成，可以開始提問。")
        while True:
            try:
                question = input("\n請輸入問句 (輸入 q 離開): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n結束")
                break
            if question.lower() in ('q', 'quit', 'exit', ''):
                print("結束")
                break
            self.answer_question(question, ERC, classifiers, loaded_model)

    def answer_question(self, question, ERC, classifiers, loaded_model):
        r = loaded_model.predict(LCQUAD.predict(classifiers, LCQUAD.tokenize(question)))
        template = dictionary[r[0]]

        if question[-1] in '?.':
            question = question[:-1]

        parsedResult = Preprocessor(question, ERC).getParsingResult()
        EF = EntityFinder(parsedResult)
        E, R, C, RR = EF.getE(), EF.getR(), EF.getC(), EF.getRR()

        dbq = DBpediaQueries()
        NamedEntity = dbq.NamedEntityExtracting(EF.E, parsedResult)
        Class = dbq.classExtracting(EF.C, parsedResult)
        Property = dbq.propertyExtracting(EF.R, parsedResult)
        if RR != []:
            Property = dbq.propertyExtracting(EF.RR, parsedResult)
        for key, listOfDup in Property.items():
            Property[key] = list(set(listOfDup))

        print("命名實體:", NamedEntity)
        print("類別實體:", Class)
        print("屬性實體:", Property)
        print("模板:", template)

        answer = []
        try:
            dbq.clearResult()
            answer, _, _ = SPARQLgeneration().SPARQLgeneration(
                NamedEntity, Property, Class, E, R, RR, C, template)
        except Exception:
            print("no answer")
        answer = list(set(answer))

        at = AnswerTypeExtractor()
        at.answerTypeExtracting(EF.getV(), question)
        ansTypeString = at.getAnswerType()

        found_answer = []
        if ansTypeString == 'Boolean' and template == 'D':
            found_answer.append('True' if True in answer else 'False')
        else:
            try:
                found_answer = answer if len(answer) > 300 else at.filterAnswer(answer)
            except Exception:
                print("沒有找到任何答案")

        print("答案型態:", ansTypeString)
        print("答案:", found_answer)


if __name__ == "__main__":
    QA_withDBpedia().main()

from Preprocessor import Preprocessor
from Preprocessor_Bert import QALD_7
from Preprocessor_Glove import Preprocessor_Glove, QALD_8
from DBpediaQueries import DBpediaQueries
from EntityFinder import EntityFinder
from AnswerTypeExtractor import AnswerTypeExtractor
from tensorflow import keras
from SPARQLgeneration import SPARQLgeneration
import numpy as np
from ERC_Tagger import ERC_Tagger
import pandas as pd
import joblib

import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"

#question = 'How many university are located in Taichung?'

    
class QA_withDBpedia():
    check_second_tag_list = {}
    stock_repeat_E = ""
    correct = True
    E_correct = True
    check_second_tag = ""
    nd_tagged=""

    
    def main(self):

        found_answer = []
        NamedEntity = {}
        Property = {}
        Class = {}


        ERC = ERC_Tagger(use_bert=False)
        
        #QALD-7
        
        classifiers = QALD_7.classifiers()  
        loaded_model = joblib.load('./model/QALD-7/svm_QALD-7')
        '''
        PG = Preprocessor_Glove
        wordsList, word_idx, wordVectors = PG.WordEmbedding(100)
        posList, pos_idx, posVectors = PG.PosEmbedding()
        classifiers = QALD_8.classifiers()
        loaded_model = joblib.load('./model/QALD-8/svm_QALD-8')
        '''
        
        question = input("Enter a sentences to test or input 1 to quit process:" + "\n")
        print("輸入的問句為:", question)
        if question == "1":
            print("輸入1，程式結束")
        if question == "":
            print('請輸入問句')
        else:
            #question = qald_quesetion['Sentence'][i]
            #去除最後一個符號
            
            test_dataset = QALD_7.tokenize(question)
            
            #wordembedding = PG.Transform2WordEmbedding(question, wordsList, word_idx)
            #posembedding = PG.Transform2PosEmbedding(question, posList, pos_idx)
            result =  QALD_7.predict(classifiers, test_dataset)
            r = loaded_model.predict(result)
            question = question[0:len(question) - 1] 
            
            pp = Preprocessor(question,ERC)
            parsedResult = []
            parsedResult = pp.getParsingResult()
            
            print("------------------------------進行標記------------------------------------------");
            st_tagged = parsedResult  
            print('第一階段tag結果:', st_tagged)
            print('------------------------------根據tag的合併單字---------------------------------')
            EF = EntityFinder(st_tagged)
            E = EF.getE()
            R = EF.getR()
            C = EF.getC()
            RR = EF.getRR()
    
            print("------------------------------尋找實體----------------------------------------")
            dbq = DBpediaQueries()
            
            print("------------------------------命名實體----------------------------------------")           
            NamedEntity = dbq.NamedEntityExtracting(EF.E, parsedResult)
            
            print("------------------------------類別實體----------------------------------------")   
            Class = dbq.classExtracting(EF.C, parsedResult)
            
            print("------------------------------屬性實體----------------------------------------")
            Property = dbq.propertyExtracting(EF.R, parsedResult)
            if RR !=[]:
                Property = dbq.propertyExtracting(EF.RR, parsedResult)
            #去除Property dict的重複值
            for key,listOfDup in Property.items():
                Property[key] = list(set(listOfDup))
            
            print("所有命名實體：",NamedEntity);
            print("所有類別實體：",Class);
            print("所有屬性實體：",Property);
            
            
            #林晉德
            print("------------------------------產生查詢語法------------------------------------")
            
            
            #QALD-7
       

            ORG_dictionary = ['A', 'AE', 'AF', 'AFI', 'B', 'BF', 'BFI', 'Bfj', 'D', 'aFJ', 'aG', 'ag', 'bfj', 'bg']
            dictionary = ['A', 'AA', 'AB', 'ABB', 'B', 'BB', 'BBB', 'Bbc', 'D', 'aBC', 'aC', 'ac', 'bbc', 'bc']
    
            '''
            #QALD-8
            result =  QALD_8.predict(classifiers, wordembedding, posembedding)
            result = np.insert(result , 5, 0, axis = 1)
            r = loaded_model.predict(result)
            ORG_dictionary =['A', 'AE', 'AF', 'AFI', 'B', 'BF', 'BFI', 'D', 'aG', 'ag', 'bfj', 'bg']
            dictionary =['A', 'AA', 'AB', 'ABB', 'B', 'BB', 'BBB', 'D', 'aC', 'ac', 'bbc', 'bc']
            '''
            
            print('模板', dictionary[r[0]])
            SP = SPARQLgeneration()
            answer = []
            number_of_query = 0
            find_triple = 0
            try:
                dbq.clearResult()
                answer, number_of_query, find_triple = SP.SPARQLgeneration(NamedEntity, Property, Class, E, R, RR, C, dictionary[r[0]])
            except Exception:
                print("no answer")
            print("所有找到的答案:", answer)
            
            answer = list(set(answer))
            
            #找出答案類型
            at = AnswerTypeExtractor()
            at.answerTypeExtracting(EF.getV(), question)
            ansTypeString = at.getAnswerType()
            print("答案型態為:", ansTypeString)
            
            if ansTypeString == 'Boolean'and dictionary[r[0]] == 'D':
                if True in answer:
                    found_answer.append('True')
                else:
                    found_answer.append('False')
            else:
                try:
                    found_answer = at.filterAnswer(answer)
                    print('found answer:' ,found_answer)
                except Exception:
                    print("沒有找到任何答案") 

if __name__ == "__main__":
    qa = QA_withDBpedia()
    qa.main()
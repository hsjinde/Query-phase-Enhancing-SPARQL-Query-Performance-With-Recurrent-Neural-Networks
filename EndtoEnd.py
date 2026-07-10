from Preprocessor import Preprocessor
from Preprocessor_Bert import LCQUAD
from DBpediaQueries import DBpediaQueries
from EntityFinder import EntityFinder
from AnswerTypeExtractor import AnswerTypeExtractor
from tensorflow import keras
from SPARQLgeneration import SPARQLgeneration
import numpy as np
from ERC_Tagger import ERC_Tagger
import pandas as pd
import joblib
import copy
import os
import time
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
class QA_withDBpedia():
    def main(self):
        '''
        found_answer = []
        NamedEntity = {}
        Property = {}
        Class = {}
        '''

        ERC = ERC_Tagger(use_bert=False)
        
        classifiers = LCQUAD.classifiers()  
        loaded_model = joblib.load('./model/LCQUAD/svm_LCQUAD')

        '''
        question = input("Enter a sentences to test or input 1 to quit process:" + "\n")
        print("輸入的問句為:", question)
        if question == "1":
            print("輸入1，程式結束")
        if question == "":
            print('請輸入問句')
        else:
        '''
        Performance = []
        data = pd.read_excel( "./answer/LCQUAD-test.xlsx")
        data = data[data['id'].notna()]
        de_index = data[data['Answer'] =='Unapplicable'].index
        data_quesetion = data.drop(de_index) 
        data_quesetion = data_quesetion.reset_index()
        data = [49,106,171,224,227,233,235,248,281,327,328,335,342,375,378,379,385,426,461,472,473,513,548,564,570,584,602]

        #for i in range(380,400):  #data_quesetion.shape[0]
        for i in data:
            found_answer = []
            NamedEntity = {}
            Property = {}
            Class = {}
            # 前處理
            question = data_quesetion['Q'][i]

            #去除最後一個符號
            test_dataset = LCQUAD.tokenize(question)
            result =  LCQUAD.predict(classifiers, test_dataset)
            r = loaded_model.predict(result)
            #wordembedding = PG.Transform2WordEmbedding(question, wordsList, word_idx)
            #posembedding = PG.Transform2PosEmbedding(question, posList, pos_idx)
            
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
            ORG_dictionary = ['A', 'AE', 'AEI', 'AF','AG', 'B', 'BF', 'BFI', 'BFJ', 'BFj', 'BfJ', 'Bfi', 'Bfj', 'D', 'aFJ', 'aG', 'afj', 'ag', 'bG', 'bfj', 'bg']
            dictionary = ['A', 'AA', 'AAB', 'AB','AC', 'B', 'BB', 'BBB', 'BBC', 'BBc', 'BbC', 'Bbb', 'Bbc', 'D', 'aBC', 'aC', 'abc', 'ac', 'bC', 'bbc', 'bc']

            
            print('模板', dictionary[r[0]])
            SP = SPARQLgeneration()
            answer = []
            number_of_query = 0
            find_triple = 0
            start = 0
            end = 0
            try:
                start = time.time()
                dbq.clearResult()
                answer, number_of_query, find_triple = SP.SPARQLgeneration(NamedEntity, Property, Class, E, R, RR, C, dictionary[r[0]])
                end = time.time()
            except:
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
                    if len(answer) > 300:
                        found_answer = answer
                    else:
                        found_answer = at.filterAnswer(answer)
                        print('found answer:' ,found_answer)
                except:
                    print("沒有找到任何答案") 

            Performance.append([i,data_quesetion['Q'][i], data_quesetion['query'][i] , E , R , C, RR, dictionary[r[0]], number_of_query, find_triple, answer, data_quesetion['Answer'][i], found_answer,end - start])
            pd.DataFrame(Performance, columns=['n','Sentence', 'query', 'E', 'R', 'C', 'RR', 'template', 'number of query', 'find triple', 'system answer', 'true answer', 'system after Q type','TIME']).to_excel('LCQUADendtoendnew_380.xlsx')

            
if __name__ == "__main__":
    qa = QA_withDBpedia()
    qa.main()


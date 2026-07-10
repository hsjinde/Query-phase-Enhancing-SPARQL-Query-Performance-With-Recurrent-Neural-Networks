from SPARQLWrapper import SPARQLWrapper, JSON
from nltk.stem import WordNetLemmatizer
import difflib
import nltk
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
class AnswerTypeExtractor:
    answerType=''
    lemmatizer = WordNetLemmatizer()
    def __init__(self):
        self.queryResult = []
    #找出答案類型
    def answerTypeExtracting(self, varible, sent):
        self.answerType=''
        boolean = False
        try:
            varible = varible[0].lower()
        except:
            varible = ''
        
        if varible == 'can' or varible == 'do' or varible == 'does' or varible == 'is' or varible == 'am' or varible == 'are' or varible == 'be' or varible == 'was' or varible == 'were':
            self.answerType='Boolean'
            boolean = True
            
        
        try:
            if not boolean:
                print(varible)
                if varible.lower()=='which' or  varible.lower() =='what' or varible.lower() == 'give' or varible.lower() == 'show' or varible.lower() == 'list' or varible.lower() == 'find' or varible.lower() == 'name':
                    self.answerType='Thing'
                elif varible.lower()=='how many' or varible.lower()=='how much' or varible.lower() =='count' or varible.lower() =='number' or varible.lower() =='how' or 'number of' in sent.lower():
                    self.answerType='Number'
                elif varible.lower()=='who' or  varible.lower() =='whom' or  varible.lower() =='whose':
                    self.answerType='Person or Organization'
                elif varible.lower()=='where':
                    self.answerType='Place'
                elif varible.lower()=='when':
                    self.answerType='Date'
                else:
                    self.answerType = 'Thing'
        except: 
            self.answerType='Thing'

        return self.answerType

    def extractent(self,p):
        if 'http' in p:
            if 'XMLSchema#' in p:
                p = p.split('http')[0]
                ent = True
            else:
                p = p.split('/')[-1]
                ent = True
        else:
            if 'xsd:' in p:
                p = p.split('xsd:')[-1]
                ent = True
            else:
                ent = False
        return ent,p
    
    #執行答案篩選查詢
    def executeSparql(self, target,spo):
        querySentence = "SELECT DISTINCT " + target + " WHERE {" + spo + "}"
        #print(querySentence)
        sparql.setQuery(querySentence)     
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        target = target.replace("?","")
        try:
            for result in results["results"]["bindings"]:
                if result[target]["value"] not in self.queryResult:
                    self.queryResult.append(result[target]["value"])
        except:
            print("didn't find results")

    
    #答案篩選條件設置
    def filterAnswer(self, ans):
        tmpAns = []
        # 刪除重複答案(利用set的屬性，set內不能出現重複答案)
        ans = list(set(ans))
        found_answer = []
        remove_list = []

        for i in range(len(ans)):
            if ans[i] == '':
                continue
            addent = True
            found_answer.append(ans[i])
            for j in range(len(ans) - (i + 1)):
                ibool, ei = self.extractent(ans[i])
                jbool, ej = self.extractent(ans[i + j + 1])
                seq = difflib.SequenceMatcher(lambda x: x in ' _,', ei.lower(), ej.lower())
                ratio = seq.ratio()

                if not (ibool and jbool):
                    if ratio > 0.9:
                        print(ei + ',' + ej)
                        print(ratio)
                        if ibool:
                            remove_list.append(ans[i + j + 1])
                        elif jbool:
                            remove_list.append(ans[i])
        for r in remove_list:
            print(r)
            found_answer.remove(r)

        found_answer = list(set(found_answer))

        #如果答案型態=人或組織 
        if self.answerType=='Person or Organization':
            for ansStr in found_answer:
                if not 'http:' in ansStr:
                    continue
                temp = '?x rdf:type dbo:Person. Filter( ?x = <'+ansStr+'>)'
                self.executeSparql("?x",temp)
                temp2 = '?x rdf:type dbo:Organization. Filter( ?x = <'+ansStr+'>)'
                self.executeSparql("?x",temp2)
            if self.getQueryResult() != []:
                tmpAns=self.getQueryResult()
            else:
                tmpAns = found_answer
        
        #如果答案型態是地點        
        elif self.answerType=='Place':
            for ansStr in found_answer:
                if not 'http:' in ansStr:
                    continue
                self.executeSparql("?x","?x rdf:type dbo:Place. Filter( ?x = <"+ansStr+">)")
            if self.getQueryResult() != []:
                tmpAns=self.getQueryResult()
            else:
                tmpAns =found_answer
        
        #如果答案型態是布林值        
        elif self.answerType=='Boolean':
            print('answerType: Boolean!!!')
            if len(found_answer)>0:
                tmpAns.append('True')
                print('True')
            else:
                tmpAns.append('False')
                print('False')
        
        #如果答案型態是日期  
        elif self.answerType=='Date':
            for ansStr in found_answer:
                if 'XMLSchema#date' in ansStr or 'XMLSchema#gMonthDay' in ansStr or 'XMLSchema#gYear' in ansStr:
                    tmpAns.append(ansStr) 
        
        #如果答案型態是數值 
        elif self.answerType=='Number': 
             check=0
             for ansStr in found_answer:
                if 'XMLSchema' in ansStr or 'xsd' in ansStr:
                    tmpAns.append(ansStr) 
                    check=1
             if check==0  :
                print('答案中不包含XMLSchema和xsd，大小為：',len(found_answer))
                if len(found_answer)>0:
                    tmpAns.append(str(len(found_answer)))
                else:
                    tmpAns.append('0')
        else:
             tmpAns = found_answer
        if tmpAns == []:
            tmpAns = ans
        self.queryResult = []

        return tmpAns    
                
    def getAnswerType(self):
        return self.answerType

    def getQueryResult(self):
        return self.queryResult


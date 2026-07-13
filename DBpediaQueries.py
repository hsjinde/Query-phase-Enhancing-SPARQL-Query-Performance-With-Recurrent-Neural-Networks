from nltk.corpus import wordnet as wn
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from LocalDbrMatcher import LocalDbrMatcher
import sqlite3
import nltk

class DBpediaQueries():
    __queryResult = []
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    QUERYPREFIX = "PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>\n" \
                  + "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" \
                  + "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n" \
                  + "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n" \
                  + "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n" \
                  + "PREFIX foaf: <http://xmlns.com/foaf/0.1/>\n" \
                  + "PREFIX dc: <http://purl.org/dc/elements/1.1/>\n" \
                  + "PREFIX dbr: <http://dbpedia.org/resource/>\n" \
                  + "PREFIX dbo: <http://dbpedia.org/ontology/>\n" \
                  + "PREFIX dbp: <http://dbpedia.org/property/>\n" \
                  + "PREFIX dbpedia: <http://dbpedia.org/> \n" \
                  + "PREFIX dbpedia2: <http://dbpedia.org/property/>\n"

    # sparql查詢結果
    __isFound = False;
    __querySentence = ""

    def __init__(self):
        # Per-instance query-result buffer. This was previously only a
        # class-level attribute (`__queryResult = []` above), so every
        # DBpediaQueries instance shared the same list and answers could leak
        # from one question to the next unless clearResult() happened to run
        # first. Initialising it here gives each instance its own buffer.
        self.__queryResult = []

    def executeSparqlSearch(self, SPARQL):
        querySentence = 'SELECT DISTINCT ?ans WHERE{'+ SPARQL +'}'
        print(querySentence)
        #try:
        self.sparql.setQuery(querySentence)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        #print(results)
        target = '?ans'
        target = target.replace("?", "")        
        for result in results["results"]["bindings"]:
            
            try:
                if 'datatype' in result[target]:
                    self.__queryResult.append(result[target]["value"]+result[target]["datatype"])
                    print('result_type:',result[target]["datatype"])
                else:
                    self.__queryResult.append(result[target]["value"])
            except Exception:
                print("didn't find results")
        self.__queryResult = list(set(self.__queryResult))
        
        #except:
            #print('sparql endpoint維修中，請稍後再試')
    
    def executeSparql_ask(self, target, spo): 
        querySentence = "ASK WHERE {" + spo + "}"
        print(querySentence)
        self.sparql.setQuery(querySentence)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        #print(results)
        target = target.replace("?", "")        
        try:
            self.__queryResult.append(results['boolean'])
        except Exception:
            print("didn't find results")
        self.__queryResult = list(set(self.__queryResult))
    
    
    def executeSparql(self, target, spo): 
        querySentence = "SELECT DISTINCT " + target + " WHERE {" + spo + "}"
        print(querySentence)
        #try:
        self.sparql.setQuery(querySentence)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        #print(results)
        target = target.replace("?", "")        
        for result in results["results"]["bindings"]:
            
            try:
                if 'datatype' in result[target]:
                    self.__queryResult.append(result[target]["value"]+result[target]["datatype"])
                    print('result_type:',result[target]["datatype"])
                else:
                    self.__queryResult.append(result[target]["value"])
            except Exception:
                print("didn't find results")
        self.__queryResult = list(set(self.__queryResult))
        #except:
            #print('sparql endpoint維修中，請稍後再試')
    # 兩個target
    def executeSparql2(self, target, target2, spo):
        querySentence = "SELECT DISTINCT " + target + " " + target2 + " WHERE { " + spo + "}"
        #print(querySentence)
        self.sparql.setQuery(querySentence)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        target = target.replace("?", "")
        target2 = target2.replace("?", "")
        try:
            for result in results["results"]["bindings"]:
                if result[target]["value"] not in self.__queryResult:
                    if result[target2]["value"] not in self.__queryResult:
                        self.__queryResult.append(result[target]["value"])
                        self.__queryResult.append(result[target2]["value"])
                        print(result[target]["value"])
                        print(result[target2]["value"])
        except Exception:
            print("didn't find results")

    # 三個target
    def executeSparql3(self, target, target2, target3, spo):
        querySentence = "SELECT DISTINCT " + target + " " + target2 + " " + target3 + " WHERE { " + spo + "}"
        #print(querySentence)
        self.sparql.setQuery(querySentence)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        target = target.replace("?", "")
        target2 = target2.replace("?", "")
        target3 = target3.replace("?", "")
        try:
            for result in results["results"]["bindings"]:
                if result[target]["value"] not in self.__queryResult:
                    if result[target2]["value"] not in self.__queryResult:
                        if result[target2]["value"] not in self.__queryResult:
                            self.__queryResult.append(result[target]["value"])
                            self.__queryResult.append(result[target2]["value"])
                            self.__queryResult.append(result[target3]["value"])
                            print(result[target]["value"])
                            print(result[target2]["value"])
                            print(result[target3]["value"])
        except Exception:
            print("didn't find results")        
    # ------------------------------------------------------------------------------
    # Name Entity
    def NERExtracting(self, w, ws, NamedEntity):  # list, list, dictionary
        urlresult = ""  # string
        entity = []  # string list
        Entity = {}  # dictionary
        count = len(w)
        for nPhrase in w:
            if nPhrase in NamedEntity:
                continue
            print("尋找消歧義頁面(dbo:wikiPageDisambiguates)")
            self.executeSparql("?o", "?s rdfs:label \"" + nPhrase + "\"@en. FILTER(regex(str(?s) , \"resource\")). "
                               + "?s dbo:wikiPageDisambiguates ?o. " +
                               "FILTER NOT EXISTS{?s rdf:type skos:Concept}.")
            if len(self.__queryResult) != 0:  # 查詢有結果
                print("***找到", nPhrase, "的消歧義頁面命名實體：", self.getQueryResult())
                for disambiguatesUrl in self.getQueryResult():
                    entity.append("<" + disambiguatesUrl + ">")
            else:
                print("***沒有" + nPhrase + "的消歧義頁面命名實體")

            print("尋找同義詞")
            for synset in wn.synsets(nPhrase):
                for lemma in synset.lemmas():
                    syn = lemma.name()
                    self.executeSparql("?s", "?s rdfs:label \"" + syn +
                                       "\"@en.FILTER(regex(str(?s) , \"resource\"))." +
                                       "FILTER NOT EXISTS{?s rdf:type skos:Concept}.")
            if len(self.__queryResult) != 0:  # 查詢有結果
                print("***找到", nPhrase, "的同義詞命名實體：", self.getQueryResult())
                for Synonym in self.getQueryResult():
                    entity.append("<" + Synonym + ">")
            else:
                print("***沒有" + nPhrase + "的同義詞命名實體")
            print("尋找從屬詞")
            for lemma in wn.lemmas(nPhrase):
                for related in lemma.derivationally_related_forms():
                    syn = related.name()
                    self.executeSparql("?s", "?s rdfs:label \"" + syn + "\"@en.FILTER(regex(str(?s) , \"resource\"))." +
                                       "FILTER NOT EXISTS{?s rdf:type skos:Concept}.")
            if len(self.__queryResult) != 0:  # 查詢有結果
                print("***找到", nPhrase, "的從屬詞命名實體：", self.getQueryResult())
                for Derivational in self.getQueryResult():
                    entity.append("<" + Derivational + ">")
            else:
                print("***沒有" + nPhrase + "的從屬詞命名實體")
            self.getQueryResult().clear()  # 清理暫存
            for url in entity:
                urlresult += url + "@"
            if urlresult != "":
                Entity[nPhrase.replace(" ", "_")] = urlresult
            entity = []
            urlresult = ""
        count -= 1
        self.__queryResult.clear()
        return Entity    
    
    # ---------N-gram在DBRDict-AB找命名實體------------------------------------------
    def ngramExtracting(self, w, n):  # 傳一個list物件w以及長度n
        self.__queryResult.clear()    
        nPhrase = ''
        nLemma = ''
        stock = ''
        #sqlA = "SELECT uri " + "FROM A WHERE label == ?" + "COLLATE NOCASE"
        #sqlB = "SELECT uri " + "FROM B WHERE label == ?" + "COLLATE NOCASE"
        sqlA = "SELECT uri " + "FROM A WHERE label == ?"
        sqlB = "SELECT uri " + "FROM B WHERE label == ?"
        Entity = {}
        entity = []
        matchedUrl = []
        ws = w  # 接傳過來的parsedResult
        count = n

        # 資料庫連線
        conn = sqlite3.connect("SQLite/DictAB.sqlite")

        while (count >= 2):  # count控制n-gram的n的大小
            for i in range(1, (len(ws) - (count - 1))):  # i控制句子中的第幾個phrase
                print(count, 'gram:')
                nPhrase = ''
                nLemma = ''
                # 前處理
                # 確認不是符號或I(代名詞)開頭
                if len(ws)-i < count:
                    continue
                if (ws[i].getWord()[0].isalpha() and ws[i].getPos() != 'PRP'):
                    for j in range(i, (i + count)):  # j在控制n-gram中的單字是否需要加上空白
                        # ->did Angela Merkel attend 第一個單字前不加上空白
                        if not j == i:  # 不是第一個字，前面不需要加空格
                            nPhrase += ' ' + ws[j].getWord()
                            nLemma += ' ' + ws[j].getLemma()
                        else:
                            nPhrase += ws[j].getWord()
                            nLemma += ws[j].getLemma()
                    if '_' in nPhrase:
                        continue

                # coreNLP會把Farmers' Almanac斷詞為Farmers ' Almanac
                # 在這邊把Farmers ' Almanac換成Farmers' Almanac
                nPhrase = nPhrase.replace(" '", "'");
                nLemma = nLemma.replace(" '", "'");

                # 找本地端的dbr
                # --------------------------SQLite 開始--------------------------------------
                # DBRDict-A 用單字找
                rsA = conn.execute(sqlA, (nPhrase,))
                print("找Resource在SQLiteA藉由Label = " + nPhrase)
                for tup in rsA:
                    for u in tup:
                        print("在SQLite找到了: ", u)
                        matchedUrl.append(u)
                    # 儲存結果
                    for url in matchedUrl:
                        self.__queryResult.append(url)
                    matchedUrl.clear()

                # DBRDict-A 用lemma找
                if nPhrase != nLemma and not self.__queryResult:
                    rsA = conn.execute(sqlA, (nLemma,))
                    print("找Resource在SQLiteA藉由Label = " + nLemma)
                    for tup in rsA:
                        for u in tup:
                            print("在SQLite找到了: ", u)
                            matchedUrl.append(u)
                    # 儲存結果
                    for url in matchedUrl:
                        self.__queryResult.append(url)
                    matchedUrl.clear()

                # DBRDict-B 用單字找
                if not self.__queryResult:
                    rsB = conn.execute(sqlB, (nPhrase,))
                    print("找Resource在SQLiteB藉由Label = " + nPhrase)
                    for tup in rsB:
                        for u in tup:
                            print("在SQLite找到了: ", u)
                            matchedUrl.append(u)
                    # 儲存結果
                    for url in matchedUrl:
                        self.__queryResult.append(url)
                    matchedUrl.clear()

                # DBRDict-B 用Lemma找
                if (nPhrase != nLemma and not self.__queryResult):
                    rsB = conn.execute(sqlB, (nLemma,))
                    print("找Resource在SQLiteB藉由Label = " + nLemma)
                    for tup in rsB:
                        for u in tup:
                            print("在SQLite找到了: ", u)
                            matchedUrl.append(u)
                    # 儲存結果
                    for url in matchedUrl:
                        self.__queryResult.append(url)
                    
                    matchedUrl.clear()  # 清理暫存    
                # SQLite 結束
                # 將結果儲存
                for url in self.__queryResult:
                    entity.append("<" + url + ">")
                self.__queryResult.clear()
                
                if not entity == []:        
                    # 如果entity不為空，代表整個gram為一個命名實體，因此用底線取代空格進行連接
                    # Angela Merkel -> Angela_Merkel
                    # if not ws[i].getEntityURL():
                    if ws[i].getEntityURL() == []:
                        # 把Angela_Merkel當作新的字把Angel取代掉
                        nPhrase = nPhrase.replace(" ", "_")
                        ws[i].__setWord__(nPhrase)  # 將第i個字用nPhrase取代
                        ws[i].__setLemma__(nPhrase)
                        ws[i].__setPos__(nPhrase)
                        ws[i].__setEntityURL__(entity)
                    # 因為前面合併了單字，所以刪除ws中被合併的單字
                    # 把Merkel從ws中刪去
                    k = i + 1
                    while ((k < (i + count)) and (k < len(ws))):
                        if ws[k].getLemma() in ws[i].getLemma():
                            ws.remove(ws[k])
                            # How War_and_Peace (and peace) have?
                        else:
                            k += 1
                    for url in entity:
                        stock += url + "@"

                    Entity[nPhrase] = stock
                    stock = ""
                    entity = []
            count -= 1
            
        print('當n = 1時只針對nn或nnp')
        if count == 1:
            for i in range(len(ws)):
                # 當n = 1 時只針對nn或nnp
                if ws[i].getPos() == "NNP" or ws[i].getPos() == "NNPS":
                    if "NN" in ws[i].getPos() and i > 0:
                        # ws[i].GetEntityURL()如果是空的代表這是還沒被處理的字
                        # 不是空的代表他是在前面的n-gram中被合併過的單字
                        if ws[i].getEntityURL() == []:
                            tmp = ws[i].getWord()
                            tmpNP = []
                            tmpNP = self.resourceExtracting(tmp)  # 查詢是否有相關的dbr
                            if tmpNP != []:  # 如果有找到 就加入pattern 然後 set entity
                                for url in tmpNP:
                                    stock += url + "@"
                                Entity[tmp] = stock

        return Entity

    # 模糊頁面
    def dism(self, uri):
        b = True
        dissentence = "ASK where{<" + uri + "> dbo:wikiPageDisambiguates  ?x }"

        self.sparql.setQuery(self.QUERYPREFIX + dissentence)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        if results == True:
            return True
        else:
            return False

    #--------------------------------------------------------------------
    def resourceExtracting(self, nnp):
        resourceExtracting_resourceSet = []
        print("resourceExtracting-尋找'" + nnp + "' 對應DBpedia resource...")
        # 找本地端的dbr
        LocalDbrMatcher.matchingLabel(nnp)
        for url in LocalDbrMatcher.getMatchedUrl():
            resourceExtracting_resourceSet.append("<" + url + ">")

        # 清空
        LocalDbrMatcher_getMatchedUrl = LocalDbrMatcher.getMatchedUrl()
        LocalDbrMatcher_getMatchedUrl.clear()

        # 沒找到就連線查詢確認
        if resourceExtracting_resourceSet == []:
            print("本地端沒找到，連線查詢確認")
            self.executeSparql("?s", "?s rdfs:label \"" + nnp + "\"@en.FILTER(regex(str(?s) , \"resource\"))." +
                              "FILTER NOT EXISTS{?s rdf:type skos:Concept}.")
        if resourceExtracting_resourceSet == []:
            self.executeSparql("?o",
                              "?s rdfs:label \"" + nnp + "\"@en.?s dbo:wikiPageRedirects ?o.FILTER(regex(str(?o) , \"resource\"))." +
                              "FILTER NOT EXISTS{?s rdf:type skos:Concept}.");

        for url in self.getQueryResult():
            if url not in resourceExtracting_resourceSet:
                resourceExtracting_resourceSet.append("<" + url + ">")
        QueryResult = self.getQueryResult()
        QueryResult.clear()
        
        # 儲存結果
        if self.getQueryResult() != []:
            for disambiguatesUrl in self.getQueryResult():
                resourceExtracting_resourceSet.append("<" + disambiguatesUrl + ">")

            QueryResult = self.getQueryResult()
            QueryResult.clear()
            #print(resourceExtracting_resourceSet)
        print("The '", nnp ,"' 對應DBpedia resource...",len(resourceExtracting_resourceSet))
        for url in resourceExtracting_resourceSet:
            print(url)
        return resourceExtracting_resourceSet
        # ------------------------------------------------------------------------------
    #find nameentity
    def NamedEntityExtracting(self, e, ws):
        sqlA = "SELECT uri " + "FROM A WHERE label == ?"
        sqlB = "SELECT uri " + "FROM B WHERE label == ?"
        Entity = {}
        entity = []
        matchedUrl = []
        lemma=""
        ws = ws  # 接傳過來的parsedResult

        for nPhrase in e:      
            for j in range(len(ws)): 
                for k in nPhrase.split(" "):# Elton John       
                    if k == ws[j].getWord():
                        lemma += ws[j].getLemma() + " "
                        break;
            lemma = lemma[:len(lemma) - 1] #拿掉最後面的空白
            

            # 資料庫連線
            conn = sqlite3.connect("SQLite/DictAB.sqlite")
            self.__queryResult.clear()
            
            # DBRDict-A 用nPhrase找
            rsA = conn.execute(sqlA, (nPhrase,))
            print("找Resource在SQLiteA藉由Label = " + nPhrase)
            for tup in rsA:
                for u in tup:
                    print("在SQLite找到了:", u)
                    matchedUrl.append(u)
                               
            # 儲存結果
            for url in matchedUrl:
                self.__queryResult.append(url)
            matchedUrl.clear()
            
            # DBRDict-A 用lemma找
            if nPhrase != lemma and not self.__queryResult:
                rsA = conn.execute(sqlA, (lemma,))
                print("找Resource在SQLiteA藉由Label = " + lemma)
                for tup in rsA:
                    for u in tup:
                        print("在SQLite找到了: ", u)
                        matchedUrl.append(u)
                # 儲存結果
                for url in matchedUrl:
                    self.__queryResult.append(url)
                matchedUrl.clear()
            
            #DBRDict-B 用nPhrase找
            if not self.__queryResult:
                rsB = conn.execute(sqlB, (nPhrase,))
                print("找Resource在SQLiteB藉由Label = " + nPhrase)
                for tup in rsB:
                    for u in tup:
                        print("在SQLite找到了: ", u)
                        matchedUrl.append(u)
                # 儲存結果
                for url in matchedUrl:
                    self.__queryResult.append(url)
                matchedUrl.clear()
            
            # DBRDict-B 用Lemma找
            if (nPhrase != lemma and not self.__queryResult):
                rsB = conn.execute(sqlB, (lemma,))
                print("找Resource在SQLiteB藉由Label = " + lemma)
                for tup in rsB:
                    for u in tup:
                        print("在SQLite找到了: ", u)
                        matchedUrl.append(u)
                # 儲存結果
                for url in matchedUrl:
                    self.__queryResult.append(url)
                
                matchedUrl.clear()  # 清理暫存  
               
            # SQLite 結束
            # 將結果儲存
            for url in self.__queryResult:
                entity.append("<" + url + ">")
                
            stock=""
            if entity==[]:
                stock += "?e@"
            else:      
                for url in entity:
                    stock += url + "@"
            entity =[]
            
            Entity[nPhrase] = stock
            stock = ""
   
            self.__queryResult.clear()
                
        return Entity #回傳字典型式
                          
    # find Property
    def propertyExtracting(self, p, ws):
        propertyExtracting_propertySet = {}
        lemma = ""
        propertyurl = []
        
        for nnn in p:
            lemma = ""
            for j in range(len(ws)):
                for nnlemma in nnn.split(" "):
                    if nnlemma == ws[j].getWord():
                        lemma += ws[j].getLemma() + " "
                        break;

            lemma = lemma[:len(lemma) - 1]
            
            self.__queryResult.clear()
            
            print("在DBpedia上搜尋:", nnn)
            self.executeSparql("?sp", "?sp rdf:type <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>." \
                               + "?sp rdfs:label ?label." \
                               + "FILTER(langMatches(lang(?label), \"EN\")).FILTER(regex(str(?label) ,\"" + nnn.replace(
                "_", " ") + "\")).")
            print(" ")
            self.executeSparql("?sp", "?sp rdfs:label \"" + nnn.replace("_", " ") \
                               + "\"@en.?sp rdf:type <http://www.w3.org/2002/07/owl#DatatypeProperty>.")
            print(" ")
            self.executeSparql("?sp", "?sp rdfs:label \"" + nnn.replace("_", " ") \
                               + "\"@en.?sp rdf:type <http://www.w3.org/2002/07/owl#ObjectProperty>.")
            print(" ")

            if len(lemma) > 0 and (lemma != nnn):
                print("也尋找原型:", lemma)
                self.executeSparql("?sp", "?sp rdf:type <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>." \
                                   + "?sp rdfs:label ?label." \
                                   + "FILTER(langMatches(lang(?label), \"EN\")).FILTER(regex(str(?label) ,\"" + lemma.replace(
                    "_", " ") + "\")).")
                print(" ")
                self.executeSparql("?sp", "?sp rdfs:label \"" + lemma.replace("_", " ") \
                                   + "\"@en.?sp rdf:type <http://www.w3.org/2002/07/owl#DatatypeProperty>.")
                print(" ")
                self.executeSparql("?sp", "?sp rdfs:label \"" + lemma.replace("_", " ") \
                                   + "\"@en.?sp rdf:type <http://www.w3.org/2002/07/owl#ObjectProperty>.")
                print(" ")

            for i in range(len(self.__queryResult)):
                propertyurl.append("<" + self.__queryResult[i] + ">")
            
               
            with sqlite3.connect('./SQLite/DictP.sqlite') as con:
                patty = pd.read_sql_query("SELECT * FROM ganswer", con=con)
    
                patty['pattern'] = patty['pattern'].fillna('000;')
                print("利用PATTY進行語意拓充")
    
                find_rel = []
                bool = patty['pattern'].str.contains(nnn)
                filter_data = patty[bool]
                filter_data = filter_data.reset_index(drop=True)
    
                for i in range(len(filter_data)):
                    if filter_data['relation_URI'][i] not in find_rel:
                        find_rel.append(filter_data['relation_URI'][i])
                print(nnn, "=> PATTY Relation Miner find relation:", find_rel)
                '''
                for i in range(len(find_rel)):
                    propertyurl.append("dbo:" + find_rel[i] + ">")
                    propertyurl.append("dbp:" + find_rel[i] + ">")
    
                for i in range(len(propertyurl)):
                    propertyurl[i] = propertyurl[i].replace("dbo:", "<http://dbpedia.org/ontology/").replace(" ", "_")
                    propertyurl[i] = propertyurl[i].replace("dbp:", "<http://dbpedia.org/property/").replace(" ", "_")
                '''
                find_patty = []
                find_patty.append(lemma)
                
                if find_patty != ['']:
                    print(find_patty)
                    for word in find_patty:
                        bool = patty['pattern'].str.contains(word)
                        filter_data = patty[bool]
                        filter_data = filter_data.reset_index(drop=True)
        
                        for i in range(len(filter_data)):
                            if filter_data['relation_URI'][i] not in find_rel:
                                find_rel.append(filter_data['relation_URI'][i])
                        print(word, "=> PATTY Relation Miner find relation:", find_rel)
                        
                        '''
                        for i in range(len(find_rel)):
                            propertyurl.append("dbo:" + find_rel[i] + ">")
                            propertyurl.append("dbp:" + find_rel[i] + ">")
                        
                        for i in range(len(propertyurl)):
                            propertyurl[i] = propertyurl[i].replace("dbo:", "<http://dbpedia.org/ontology/").replace(" ", "_")
                            propertyurl[i] = propertyurl[i].replace("dbp:", "<http://dbpedia.org/property/").replace(" ", "_")
                        '''
                        for i in range(len(find_rel)):
                            if not find_rel[i] in propertyurl:
                                propertyurl.append('<' + find_rel[i] + '>')
                
                #if len(propertyurl) < 1:
                 #   propertyurl = "?p"
                if len(propertyurl) < 1:
                    propertyurl.append("?p")
                    propertyExtracting_propertySet[nnn.replace("_", " ")] = propertyurl
                else:
                    propertyExtracting_propertySet[nnn.replace("_", " ")] = propertyurl
                
                print("單字",nnn)
                print("***",propertyExtracting_propertySet)
                
                
                propertyurl=[]
                self.__queryResult.clear()
        return propertyExtracting_propertySet    
        # 輸出為propertyurl(資料型態為list,包含所有找到的property的url)
        # 執行property Extracting
        # property_Extracting(ws)

    #------------------------------------------------------------------------------
    #Class entity
    def classExtracting(self, c, ws):  # list list
        classExtracting_classSet = {}
        classurl = ""
        lemma = ""

        for nn in c:
            n = nltk.word_tokenize(nn)
            for j in range(len(ws)): #找原型
                for nn_tok in n:
                    if nn_tok == ws[j].getWord():
                        #晉德 qald-9 test第61句有問題
                        try:
                            lemma +=  ws[j].getLemma() + ' '
                        except Exception:
                            print('error')
                        print(lemma)
                        break;
            print("尋找" + nn + " 對應DBpedia class(SC)...")
            LocalDbrMatcher.matchingClassLabel(nn)  # 找本地端的dbo
            #晉德 qald-9 test第61句有問題
            try:
                if (lemma != "" and lemma != nn):
                    print("尋找原型" + lemma + " 對應DBpedia class(SC)...")
                    LocalDbrMatcher.matchingClassLabel(lemma)
            except Exception:
                print('error')
                
            # 如果查詢有結果就將結果儲存
            if (LocalDbrMatcher.getMatchedUrl()):
                for url in LocalDbrMatcher.getMatchedUrl():
                    classurl += "<" + url + ">@"
                classExtracting_classSet[nn] = classurl
                LocalDbrMatcher.getMatchedUrl().clear()
                classurl = ""
                print("The '" + nn + "' 對應DBpedia class(SC):", len(classExtracting_classSet))
                print(classExtracting_classSet)
            else:
                print("尋找同義詞對應DBpedia class(SC)...")
                for synset in wn.synsets(nn):
                    for lemma in synset.lemmas():
                        syn = lemma.name()
                        LocalDbrMatcher.matchingClassLabel(syn)

                print("尋找從屬詞對應DBpedia class(SC)...")
                for lemma in wn.lemmas(nn):
                    for related in lemma.derivationally_related_forms():
                        syn = related.name()
                        LocalDbrMatcher.matchingClassLabel(syn)
                if (not LocalDbrMatcher.getMatchedUrl()):
                    print("找不到" + nn + " 對應的class(SC)")
                    classExtracting_classSet[nn] = '?C'
                else:
                    # 先在迴圈內累加所有比對到的 class URI,迴圈「外」才 clear;
                    # 若在迭代同一個 list 時就 clear,迭代會在第一筆後中止,
                    # 導致同義詞/衍生詞比對到的其餘 class 被丟棄(對照上方 if 分支的正確寫法)。
                    for url in LocalDbrMatcher.getMatchedUrl():
                        classurl += "<" + url + ">@"
                    classExtracting_classSet[nn] = classurl
                    LocalDbrMatcher.getMatchedUrl().clear()
                    classurl = ""
                    print("The '" + nn + "' 對應DBpedia class(SC):", len(classExtracting_classSet))
                    #print(classExtracting_classSet)
        return classExtracting_classSet

    def getQueryResult(self):
        return self.__queryResult
    def clearResult(self):
        return self.__queryResult.clear()
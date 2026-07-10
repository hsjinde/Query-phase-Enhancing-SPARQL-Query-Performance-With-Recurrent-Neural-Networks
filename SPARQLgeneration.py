'''
question = 'For which games are Sam Loyd and Eric Schiller both famous?'

Class = {}
E = ['Sam Loyd', 'Eric Schiller']
R = []
C = []
RR = ['famous']

NamedEntity = {'Sam Loyd': '<http://dbpedia.org/resource/Sam_Loyd>@',
 'Eric Schiller': '<http://dbpedia.org/resource/Eric_Schiller>@'}

Property = {'famous': ['<http://dbpedia.org/property/famousResidents>',
  '<http://dbpedia.org/property/famousPact>',
  '<http://dbpedia.org/property/nearFamousVillage>',
  '<http://dbpedia.org/property/famousPeople>',
  '<http://dbpedia.org/property/famousPersonality>',
  '<http://dbpedia.org/property/famousFreerunningTeams>',
  '<http://dbpedia.org/property/famousPrat>',
  '<http://dbpedia.org/property/famousFor>',
  '<http://dbpedia.org/property/famousTemple>',
  '<http://dbpedia.org/property/famousFlights>',
  '<http://dbpedia.org/property/famousPract.>',
  '<http://dbpedia.org/property/famousPract>',
  '<http://dbpedia.org/ontology/battle>',
  '<http://dbpedia.org/ontology/knownFor>',
  '<http://dbpedia.org/property/famousChowk>']}

Property = {'famous': [
  '<http://dbpedia.org/property/famousPact>',
  '<http://dbpedia.org/property/famousFor>',
  '<http://dbpedia.org/ontology/knownFor>',]}

template = 'AA'
'''


'''
question = 'In which films did Julia Roberts as well as Richard Gere play?'

E = ['Julia Roberts', 'Richard Gere']
R = ['play']
C = ['films']
RR = []
NamedEntity = {'Julia Roberts': '<http://dbpedia.org/resource/Julia_Roberts>@',
 'Richard Gere': '<http://dbpedia.org/resource/Richard_Gere>@'}

Property = {'play':['<http://dbpedia.org/ontology/starring>',
            '<http://dbpedia.org/ontology/college>',
            '<http://dbpedia.org/property/play>']}
Class = {'films': '<http://dbpedia.org/ontology/Film>@<http://dbpedia.org/ontology/FilmFestival>@'}
template = 'BBB'
'''
'''
question = 'What is the alma mater of the scientist who is known for Rational analysis'

E = ['Rational analysis']
R = ['alma mater', 'known']
RR= []
C = ['scientist']
NamedEntity = {'Rational analysis': '<http://dbpedia.org/resource/Rational_analysis>@'}
Property = {'alma mater': ['<http://dbpedia.org/property/almaMaters>',
  '<http://dbpedia.org/ontology/almaMater>',
  '<http://dbpedia.org/property/almaMater>'],
 'known': ['<http://dbpedia.org/property/asKnownAs>',
  '<http://dbpedia.org/ontology/knownFor>',
  '<http://dbpedia.org/property/knownAs>']}
Class = {'scientist': '<http://dbpedia.org/ontology/Scientist>@'}
template = 'bbc'
'''
'''
question = 'Is camel of the chordate phylum'
E= ['camel', 'chordate']
R = ['phylum']
C=[]
RR= []

NamedEntity = {'camel': '<http://dbpedia.org/resource/Camel>@',
 'chordate': '<http://dbpedia.org/resource/Chordate>@'}
Property = {'phylum': ['<http://dbpedia.org/ontology/phylum>',
  '<http://dbpedia.org/property/unrankedPhylum>',
  '<http://dbpedia.org/property/phylum>',]}
Class = {}
template = 'D'
'''

from DBpediaQueries import DBpediaQueries
import copy
class SPARQLgeneration:

    def SPARQLgeneration(self, NamedEntity, Property, Class, E, R, RR, C, template):
        self.NamedEntity = NamedEntity
        self.Property = Property
        self.Class = Class
        self.E = copy.deepcopy(E)
        self.R = copy.deepcopy(R)
        self.C = copy.deepcopy(C)
        self.ans = []
        self.query_number = 0
        self.Tolerance = []
        count = len(template)
        
        if RR !=[]:
            self.R = copy.deepcopy(RR)
        
        for i, label in enumerate(template):
            if label =='A':
                globals()['Triple'+str(i)] = self.FunA()
            elif label == 'a':
                globals()['Triple'+str(i)] = self.Funa()
            elif label=='B':
                globals()['Triple'+str(i)] = self.FunB()
            elif label == 'b':
                globals()['Triple'+str(i)] = self.Funb()
            elif label == 'C':
                globals()['Triple'+str(i)] = self.FunC()
            elif label == 'c':
                globals()['Triple'+str(i)] = self.Func()
            elif label=='D':
                globals()['Triple'+str(i)] = self.FunD()    
            else:
                print(label)
                print('some mistakes')
        
        #將triple組合成SPARQL
        S =[]
        if count == 1:
            S = self.C1()
       
        elif count == 2:
            S = self.C2()
            if S ==[]:
                S = self.C1()

        elif count == 3:
            S = self.C3()
            if S ==[]:
                S = self.C2()
            if S ==[]:
                S = self.C1()
        
        S = list(set(S))
        print('number of Query : ',len(S))
        print('find triple : ',self.query_number)
        
        if len(S) > 50000:
            #return self.ans, len(S) , self.query_number
            S = self.Tolerance
        
        dbq = DBpediaQueries()
        dbq.clearResult()
        result_set = []
        for i in S:
            if '?ans' in i:
                dbq.executeSparql('?ans', i)
            elif '?x' in i:
                dbq.executeSparql('?x', i)
            else:
                dbq.executeSparql_ask('', i)
            
            re = copy.deepcopy(dbq.getQueryResult())
            result_set.append(re)
            dbq.clearResult()
        for i in result_set:
            if i != []:
                for j in i:
                    self.ans.append(j)
        return self.ans, len(S), self.query_number
    
    def C1(self):
        S=[]
        for i in globals()['Triple0']:
            S.append(i)
        return S
    
    def C2(self):
        S=[]
        for i in globals()['Triple0']:
            for j in globals()['Triple1']:
                SPARQL = i+ j
                S.append(SPARQL)   
        return S
    def C3(self):
        S=[]
        for i in globals()['Triple0']:
            for j in globals()['Triple1']:
                for k in globals()['Triple2']:
                    SPARQL = i+ j+ k
                    S.append(SPARQL)
        return S
    def Looking_Triple(self, target, temp):
        Triple = []
        dbq = DBpediaQueries()
        for t in temp:
            dbq.clearResult()
            dbq.executeSparql(target , t)
            re = []
            self.query_number +=1
            re = copy.deepcopy(dbq.getQueryResult())
            dbq.clearResult()
            if re != []:
                Triple.append(t)
                self.Tolerance.append(t)
        return Triple
    
    def FunA(self):             
        Triple = []
        print('篩選有效的RDF triple...')
        for i, entity in enumerate(self.E):
            temp = []
            for relation in self.R:
                e = self.NamedEntity.get(entity).split('@')        
                e.pop(len(e)-1) #去掉最後一個空白，split('@')後會多一個空白欄位
                r = self.Property.get(relation)
                for uri_e in e:
                    for uri_r in r:
                      triple = uri_e + ' '+ uri_r+ ' ?ans.' 
                      temp.append(triple)
            temp = list(set(temp))
            Triple = self.Looking_Triple('?ans', temp)
            if Triple != []:
                self.E.pop(i)
                break
        return Triple
    
    def Funa(self):             
        Triple = []
        print('篩選有效的RDF triple...')
        for i, entity in enumerate(self.E):
            temp = []
            for relation in self.R:
                e = self.NamedEntity.get(entity).split('@')        
                e.pop(len(e)-1) #去掉最後一個空白，split('@')後會多一個空白欄位
                r = self.Property.get(relation)
                for uri_e in e:
                    for uri_r in r:
                      triple = uri_e + ' '+ uri_r+ ' ?x.' 
                      temp.append(triple)
            temp = list(set(temp))
            Triple = self.Looking_Triple('?x', temp)
            if Triple != []:
                self.E.pop(i)
                break
        return Triple
    
    def FunB(self):
        if self.C !=[]:
            for i in self.C:
                Triple = [] #用來裝所有triples
                classes = self.Class.get(i).split('@')
                classes.pop(len(classes)-1) #去掉最後一個空白，split('@')後會多一個空白欄位
                for c in classes:
                    if c =='?C':
                        print('未比對到類別實體')
                        triple = '?ans rdf:type ?C.'
                    else:
                        print('有比對到類別實體:',c)
                        triple = '?ans rdf:type ' + c +'.' #將Class字典找到的實體都產生SPARQL(?ans，type，C)
                    Triple.append(triple)
            self.C.pop(0) 
        else:
            Triple = []
            print('篩選有效的RDF triple...')
            for i, entity in enumerate(self.E):
                temp = []
                for relation in self.R:
                    e = self.NamedEntity.get(entity).split('@')        
                    e.pop(len(e)-1) #去掉最後一個空白，split('@')後會多一個空白欄位
                    r = self.Property.get(relation)
                    for uri_e in e:
                        for uri_r in r:
                          triple = '?ans '+ uri_r+ ' '+ uri_e+ '.' 
                          temp.append(triple)
                temp = list(set(temp))
                Triple = self.Looking_Triple('?ans', temp)
                if Triple != []:
                    self.E.pop(i)
                    break
        return Triple    
    
    def Funb(self):           
        if self.C !=[]:
            for i in self.C:
                Triple = [] #用來裝所有triples
                classes = self.Class.get(i).split('@')
                classes.pop(len(classes)-1) #去掉最後一個空白，split('@')後會多一個空白欄位
                for c in classes:
                    if c =='?C':
                        print('未比對到類別實體')
                        triple = '?x rdf:type ?C.'
                    else:
                        print('有比對到類別實體:',c)
                        triple = '?x rdf:type ' + c +'.' #將Class字典找到的實體都產生SPARQL(?ans，type，C)
                    Triple.append(triple)
            self.C.pop(0) 
        else:
            Triple = []
            print('篩選有效的RDF triple...')
            for i, entity in enumerate(self.E):
                temp = []
                for relation in self.R:
                    e = self.NamedEntity.get(entity).split('@')        
                    e.pop(len(e)-1) #去掉最後一個空白，split('@')後會多一個空白欄位
                    r = self.Property.get(relation)
                    for uri_e in e:
                        for uri_r in r:
                          triple = '?x '+ uri_r+' '+uri_e+ '.' 
                          temp.append(triple)
                temp = list(set(temp))
                Triple = self.Looking_Triple('?x', temp)
                if Triple != []:
                    self.E.pop(i)
                    break
        return Triple   
        
    def FunC(self):             
        Triple = []
        for relation in self.R:
            r = self.Property.get(relation)
            for uri_r in r:
                triple =  '?ans '+ uri_r +' ?x.' 
                Triple.append(triple)
                               
        self.R.pop(0) 
        return Triple 
        
    def Func(self):             
        Triple = []
        for relation in self.R:
            r = self.Property.get(relation)
            for uri_r in r:
                triple =  '?x '+ uri_r +' ?ans.' 
                Triple.append(triple)
                               
        self.R.pop(0) 
        return Triple 
        
    def FunD(self):                    
        Triple = []
        try:
            E1 = self.E.pop()
            E2 = self.E.pop()
        except:
            return Triple
        
        e1 = self.NamedEntity.get(E1).split('@')
        e1.pop(len(e1)-1)
        
        e2 = self.NamedEntity.get(E2).split('@')
        e2.pop(len(e2)-1)
        for relation in self.R:
            r = self.Property.get(relation)
            for uri_e1 in e1:
                for uri_e2 in e2:
                    for uri_r in r:
                        triple = uri_e1 + ' '+ uri_r+ ' '+uri_e2 +'.'
                        Triple.append(triple)
                        triple = uri_e2 + ' '+ uri_r+ ' '+uri_e1 +'.'
                        Triple.append(triple)
        return Triple
    
    
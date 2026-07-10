import nltk
import sqlite3
class LocalDbrMatcher():
    matchedUrl = []
    
    def matchingClassLabel(dboClass): #string
        line = ""
        tmpStr = []
        #StarChar = list(dboClass)      
        dboClass = dboClass.lower()
        dboclass_tok = nltk.word_tokenize(dboClass)
        #print('aaaaaa',dboclass_tok)
        print("在本地端找(class) dbo by label  = " + dboClass + "...")
        print("SQLite/dbo_class.txt")
        fis = open('SQLite/dbo_class.txt', 'r', encoding='utf-8')
        for line in fis:
            tmpStr = (line.split('→'))
            tmpStr[2] = tmpStr[2][:-1]
            if (tmpStr[1] == dboClass):
                print("找到 " + tmpStr[2])
                LocalDbrMatcher.matchedUrl.append(tmpStr[2])
            for C in dboclass_tok:
                    if C in tmpStr[2].lower():
                        print("找到 " + tmpStr[2])
                        LocalDbrMatcher.matchedUrl.append(tmpStr[2])
        fis.close()
        
    #-------------------------------------------------------------------------------
    def matchingLabel(nnp): #SQLite A
        if(nnp[0].isalpha() and "?" not in nnp):
            sql = "SELECT uri " + "FROM A WHERE label == ?" 
            if(nnp[0].isalpha()):
                conn = sqlite3.connect("SQLite/DictAB.sqlite")
                rsA = conn.execute(sql, (nnp,))
                print("找Resource在SQLiteA藉由Label =",nnp)         
                for tup in rsA:
                    for u in tup:
                        print("在SQLite找到了: ", u)
                        LocalDbrMatcher.matchedUrl.append(u)
                
                conn.close()

    def getMatchedUrl():
        return LocalDbrMatcher.matchedUrl
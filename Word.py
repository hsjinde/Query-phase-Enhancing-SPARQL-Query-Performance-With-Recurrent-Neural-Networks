class Word():
    def __init__(self, w, l, p, e):
        self.__word = ''
        self.__lemma = ''
        self.__pos = ''
        self.__entityUrl = []
        self.__setWord__(w)
        self.__setLemma__(l)
        self.__setPos__(p)
        self.__setERC__(e)

    def __setWord__(self, s):
        self.__word = s

    def __setLemma__(self, l):
        self.__lemma = l

    def __setPos__(self, p):
        self.__pos = p
    
    def __setERC__(self, e):
        self.__erc = e

    def __setEntityURL__(self, s=None):
        for url in (s or []):
            if url not in str(self.__entityUrl):
                self.__entityUrl.append(url)

    # ---------------------------------------------------------

    def getWord(self):
        return self.__word

    def getLemma(self):
        return self.__lemma

    def getPos(self):
        return self.__pos

    def getEntityURL(self):
        return self.__entityUrl

    def getERC(self):
        return self.__erc
    
    


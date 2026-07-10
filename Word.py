class Word():
    def __init__(self, w, l, p, e):
        self.__word = ''
        self.__lemma = ''
        self.__pos = ''
        self.__entityUrl = []
        self.__classUrl = []
        self.__properUrl = []
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

    def __setClassURL__(self, s=[]):
        for url in s:
            if url not in str(self.__classUrl):
                self.__classUrl.append(url)

    def __setEntityURL__(self, s=[]):
        for url in s:
            if url not in str(self.__entityUrl):
                self.__entityUrl.append(url)

    def __setProperURL__(self, s=[]):
        for url in s:
            if url not in str(self.__properUrl):
                self.__properUrl.append(url)

    # ---------------------------------------------------------

    def getWord(self):
        return self.__word

    def getLemma(self):
        return self.__lemma

    def getPos(self):
        return self.__pos

    def getEntityURL(self):
        return self.__entityUrl

    def getClassURL(self):
        return self.__classUrl

    def getProperURL(self):
        return self.__properUrl
    
    def getERC(self):
        return self.__erc
    
    


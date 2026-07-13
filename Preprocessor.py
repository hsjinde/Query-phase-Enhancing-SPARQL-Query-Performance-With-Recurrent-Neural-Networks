from nltk.stem import WordNetLemmatizer
from ERC_Tagger import ERC_Tagger
import nltk
from Word import Word
from CaculateEntityTag import combineEntity_Tag
import string

class Preprocessor():
    __word = ""
    __lemma = ""
    __pos = ""
    # 句中名詞/專有名詞/動詞
    __querySentence = []

    def __init__(self, question, ERC_TAGGER:ERC_Tagger):
        self.__querySentence = []
        sentence = question

        # tokenize
        sent = sentence.strip()
        if sent and sent[-1] in string.punctuation:
            sent = sent[:-1].strip()
        punt = ',?'
        for p in punt:
            if p in sent:
                sent = sent.strip().replace(p, '')
        tokenized_sentence = sent.split(' ')

        # ERC
        # 開始進行第一階段標記
        print("### 進行第一階段標記 ###")
        erc_tagged = ERC_TAGGER.predictERCtag(sentence)
        print('第一階段tag結果:', erc_tagged)
        print('### 根據tag的合併單字 ###')
        ce, cn = combineEntity_Tag(erc_tagged)
        n_w = 0
        cwordlist = []
        cerctagged = []
        for j in cn:
            cword = ''
            for s in tokenized_sentence[n_w:n_w + j]:
                cword += s + ' '
            n_w += j
            cwordlist.append(cword[:-1])
        tokenized_sentence = cwordlist

        for e in ce.split('/'):
            cerctagged.append(e.split('-')[0])
        erc_tagged = cerctagged

        # lemma
        Lemma = []
        lemmatizer = WordNetLemmatizer()

        def lemmatize(word):
            lemma = lemmatizer.lemmatize(word, 'v')
            if lemma == word:
                lemma = lemmatizer.lemmatize(word, 'n')
            return lemma

        Lemma = [lemmatize(token) for token in tokenized_sentence]

        # Pos
        Pos = []
        postag = nltk.pos_tag(tokenized_sentence)
        # 取出pos成為一個list
        for i in range(len(tokenized_sentence)):
            Pos.append(postag[i][1])

        # 把資料裝進Word    
        for i in range(len(tokenized_sentence)):
#            if i == 0:
#                self.__querySentence.append(Word('?temp', '?temp', '?temp', '?temp'))
            newWord = Word(tokenized_sentence[i], Lemma[i], Pos[i], erc_tagged[i])
            self.__querySentence.append(newWord)

    def getParsingResult(self):
        for parsedResult in self.__querySentence:
            print('Word=[', parsedResult.getWord(), ']-Lemma=', parsedResult.getLemma(), ', Pos=',
                  parsedResult.getPos(), ', ERC=', parsedResult.getERC())
        return self.__querySentence    

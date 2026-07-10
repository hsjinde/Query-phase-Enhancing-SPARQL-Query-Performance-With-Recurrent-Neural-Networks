from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import nltk
maxlen = 20 

class Preprocessor_Glove():
    def WordEmbedding(emb_size):
        wordVectors = [ np.zeros(emb_size, dtype=np.float32) , np.random.randn(emb_size).astype(np.float32)]
        wordsList = ['-pad-', '-oov-']
        glove_file = open('./Embedding/'+ 'glove.6B.'+ str(emb_size) +'d.txt' ,encoding="utf8")
        for line in glove_file:
            word, coefs = line.split(maxsplit=1)
            coefs = np.fromstring(coefs, "f", sep=" ")
            wordsList.append(word)
            wordVectors.append(coefs)
        
        word_idx = {w: i for i, w in enumerate(wordsList)}
        #vocab_size = len(wordsList)
        return wordsList, word_idx, wordVectors
    
    
    def Transform2WordEmbedding(Sentence, wordsList, word_idx):
        wordembedding = []
        temp = []
        words = nltk.word_tokenize(Sentence)
        for word in words:
            word = str.lower(word)
            if (word in wordsList):
                temp.append(word_idx[word])
            else:
                temp.append("1")
        wordembedding.append(temp)
        wordembedding = pad_sequences(wordembedding, padding='post', maxlen=maxlen)
        return wordembedding
    
    def PosEmbedding():
        pos_file = open('./Embedding/pos_emb_win5_size20.txt', encoding="utf8")
        posList = ['-pad-']
        posVectors = [np.zeros(20, dtype=np.float32)]
        for line in pos_file:
            pos, coefs = line.split(maxsplit=1)
            coefs = np.fromstring(coefs, "f", sep=" ")
            posList.append(pos)
            posVectors.append(coefs)
        #posVectors = np.asarray(posVectors)
        pos_idx = {p: i for i, p in enumerate(posList)}
        return posList, pos_idx, posVectors
    
    def Transform2PosEmbedding(Sentence, posList, pos_idx):
        x_pos = []
        words = nltk.word_tokenize(Sentence)
        pos_tags =nltk.pos_tag(words)
        temp = []
        for word,pos in pos_tags:
            temp.append(pos)
        x_pos.append(temp)
        posembedding = []
        for line in x_pos:
            temp = []
            for tag in line:
                temp.append(pos_idx[tag])
            posembedding.append(temp)
        posembedding = pad_sequences(posembedding, padding='post', maxlen=maxlen)
        return  posembedding
        
class QALD_8():
    def classifiers():
        from tensorflow import keras
        classifiers = []
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_0.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_1.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_2.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_3.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer2_4.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_5.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_6.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_7.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_8.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_9.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-8/QALD-8_BiLSTM_pos_Layer1_10.h5"))
        return classifiers
             
    def predict(classifiers, test_wordembedding, test_posembedding):
        X = [test_wordembedding, test_posembedding]
        number_of_x = np.array(test_wordembedding).shape[0]
        result = np.zeros((number_of_x, len(classifiers)))
        for i in range(len(classifiers)):
            for j in range(number_of_x):    
                result[j][i] = classifiers[i].predict(X)[j][0]
        return result

class QALD_9():
    def classifiers():
        from tensorflow import keras
        classifiers = []
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer3_0.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer1_1.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer1_2.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer1_3.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer2_4.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer1_5.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer1_6.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer1_7.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer1_8.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer1_9.h5"))
        classifiers.append(keras.models.load_model("./model/QALD-9/QALD-9_BiLSTM_Layer1_10.h5"))

        return classifiers
             
    def predict(classifiers, test_wordembedding, test_posembedding):
        X = [test_wordembedding, test_posembedding]
        number_of_x = np.array(test_wordembedding).shape[0]
        result = np.zeros((number_of_x, len(classifiers)))
        for i in range(len(classifiers)):
            for j in range(number_of_x):    
                result[j][i] = classifiers[i].predict(X)[j][0]
        return result
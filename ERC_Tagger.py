import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow import keras

'''tensorflow keras'''
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import layers
from tensorflow.keras.layers import LayerNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Reshape
import tensorflow_addons as tfa
from CRF import CRF
from transformers import  AutoTokenizer, TFAutoModel
from CaculateEntityTag import calculate_tag_acc
import nltk
import pandas as pd
import numpy as np
import os

class ERC_Tagger:
    def __init__(self, use_bert:bool=False):
        # 參數設定
        self.use_bert = use_bert
        # 參數設定
        self.BASE_DIR = './data/'
        self.EMBED_DIR = os.path.join(self.BASE_DIR, 'embedding/')
        self.GLOVE_DIR = os.path.join(self.EMBED_DIR, 'glove.6B/')
        self.VOCAB_DIR = os.path.join(self.BASE_DIR, 'vocab/')
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'lcquad/')# LCQUAD
        self.MODEL_DIR = './model/ERC/'
        DATA, self.MAX_LENGTH = self.read_data(os.path.join(self.DATA_DIR, 'LCQUAD.xlsx'), sh_name='LCQUAD')
        self.erc2idx = {"<PAD>": 0, "V-B": 1, "V-I": 2, "V-E": 3, "R-B": 4, "R-I": 5, "R-E": 6, "E-B": 7,
                        "E-I": 8, "E-E": 9, "C-B": 10, "C-I": 11, "C-E": 12, "N": 13, "CR-B": 14, "CR-I": 15,
                        "CE-B": 16, "CE-I": 17, "ER-B": 18, "ER-I": 19, "VR-B": 20, "VR-I": 21,
                        "RR-B": 22, "RR-I": 23, "L-B": 24, "L-I": 25}

        if not use_bert:
            print('loading GLOVE ...')
            self.EMBEDDING_DIM = 100  # embedding dim
            vocab_path_list = ['lcquad-word.vocab', 'lcquad-pos.vocab']
            self.word2idx, self.pos2idx = self.vocab_to_Index(vocab_path_list)
            self.wordVectors = self.get_WordEmbedding(self.EMBEDDING_DIM)
            self.posVectors = self.get_PosEmbedding()
            self.model_path = '1ERC_LCQUAD0.957_250ep_1layer_bilstmCRF.h5'
        else:
            print('loading BERT ...')
            vocab_path_list = ['lcquad-pos.vocab']
            self.pos2idx = self.vocab_to_Index(vocab_path_list)[0]
            self.auTokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
            self.posVectors = self.get_PosEmbedding()
            self.model_path = 'BERT_ERC_LCQUAD0.977_250ep_1layer_bilstmCRF.h5'

    def transform_feature(self, sentence:str):
        import string
        sent = sentence.strip()
        if sent[-1] in string.punctuation:
            sent = sent[:-1].strip()
        punt = ',?'
        for p in punt:
            if p in sent:
                sent = sent.strip().replace(p,'')
        w_list = sent.split(' ')
        pos_list = [e[1] for e in nltk.pos_tag(w_list)]
        word_num = len(w_list)
        if self.use_bert:
            Xids = np.zeros((1, self.MAX_LENGTH * 2))
            Xmask = np.zeros((1, self.MAX_LENGTH * 2))
            Xids[0, :], Xmask[0, :] = self.bert_token(w_list, self.MAX_LENGTH*2)
            train_pos = [self.pos2idx[p] for p in pos_list]
            train_pos = pad_sequences([train_pos], maxlen=self.MAX_LENGTH*2, value=0, padding='post')
            output = [Xids, Xmask, train_pos, w_list]
        else:
            train_word= [self.word2idx[w] if w in self.word2idx.keys() else self.word2idx['<oov>'] for w in w_list]
            train_pos = [self.pos2idx[p] for p in pos_list]
            train_word = pad_sequences([train_word], maxlen=self.MAX_LENGTH, value=0, padding='post')
            train_pos = pad_sequences([train_pos], maxlen=self.MAX_LENGTH, value=0, padding='post')
            output = [train_word, train_pos, w_list]
        return output, word_num

    def predictERCtag(self, sentence):
        feature, word_num = self.transform_feature(sentence)
        model = self.load_model(self.model_path)
        trans_action = {i: t for t, i in self.erc2idx.items()}
        if self.use_bert:
            pre_erc = self.logits_to_tokens(model.predict([feature[0], feature[1], feature[2]]), trans_action)
            w_list = feature[3]
        else:
            pre_erc = self.logits_to_tokens(model.predict([feature[0], feature[1]]), trans_action)
            w_list = feature[2]
        if len(pre_erc[0]) < word_num:
            for _ in range(word_num-len(pre_erc[0])):
                pre_erc[0].append('N')
                
        return pre_erc[0]


    def read_data(self, csv_path: str = '../data/LCQUAD/LCQUAD.xlsx', sh_name: str = ''):
            print("reading csv file:", csv_path, '\n')
            if sh_name == '':
                lcquad_df = pd.read_excel(csv_path)
            else:
                lcquad_df = pd.read_excel(csv_path, sheet_name=sh_name)

            erc = lcquad_df["ERC"]
            word_erc_list = []
            max_len = 0
            for i, s in enumerate(erc):
                word = []
                seq_w = ''
                seq_e = ''
                tag = []
                # print(i)
                # print(s)
                for j in s.strip().split(' '):
                    # if j.split('/')[1] not in ['V-B','V-I', 'E-B', 'E-I','R-B', 'R-I', 'C-B', 'C-I', 'N']:
                    #     print(i)
                    #     print(j.split('/'))
                    if len(j.split('/')) != 2:
                        s = ''
                        for k in j.split('/')[:-1]:
                            s += k + '/'
                        # print(s[:-1])
                        word.append(s[:-1])
                        seq_w += s[:-1] + ' '

                    else:
                        word.append(j.split('/')[0])
                        seq_w += j.split('/')[0] + ' '
                    tag.append(j.split('/')[-1])
                    seq_e += j.split('/')[-1] + ' '
                if len(word) > max_len:
                    max_len = len(word)
                pos = [e[1] for e in nltk.pos_tag(word)]
                word_erc_list.append([word,pos,tag])

            return word_erc_list, max_len

    def transform_traindata(self, csv_path: str = '../data/LCQUAD/LCQUAD.xlsx', sh_name: str = '', shuffle:bool=False):
        data, maxl = self.read_data(csv_path, sh_name=sh_name)
        if shuffle:
            import random
            random.shuffle(data)
        train_word = []
        train_pos = []
        train_y = []
        word_num =[]
        for sent in data:
            word_num.append(len(sent[0]))
            train_word.append([self.word2idx[w] if w in self.word2idx.keys() else self.word2idx['<oov>'] for w in sent[0]])
            train_pos.append([self.pos2idx[p] for p in sent[1]])
            train_y.append([self.erc2idx[f] for f in sent[2]])

        train_word = pad_sequences(train_word, maxlen=self.MAX_LENGTH, value=0, padding='post')
        train_pos = pad_sequences(train_pos, maxlen=self.MAX_LENGTH, value=0, padding='post')
        train_y = pad_sequences(train_y, maxlen=self.MAX_LENGTH, value=0, padding='post')

        print("word data dim", train_word.shape)
        print("pos data dim", train_pos.shape)
        print("Y label(predict action) dim", train_y.shape)
        return train_word, train_pos, train_y, word_num

    def transform_BERTtraindata(self, csv_path: str = '../data/LCQUAD/LCQUAD.xlsx', sh_name: str = '', shuffle:bool=False):
        data, maxl = self.read_data(csv_path, sh_name=sh_name)
        if shuffle:
            import random
            random.shuffle(data)

        train_pos = []
        train_y = []
        word_num =[]
        Xids = np.zeros((len(data), self.MAX_LENGTH*2))
        Xmask = np.zeros((len(data), self.MAX_LENGTH*2))

        for i,sent in enumerate(data):
            Xids[i, :], Xmask[i, :] = self.bert_token(sent[0], self.MAX_LENGTH*2)
            word_num.append(len(sent[0]))
            train_pos.append([self.pos2idx[p] for p in sent[1]])
            train_y.append([self.erc2idx[f] for f in sent[2]])

        train_pos = pad_sequences(train_pos, maxlen=self.MAX_LENGTH*2, value=0, padding='post')
        train_y = pad_sequences(train_y, maxlen=self.MAX_LENGTH*2, value=0, padding='post')

        print("word data dim", Xids.shape)
        print("pos data dim", train_pos.shape)
        print("Y label(predict action) dim", train_y.shape)
        return Xids, Xmask, train_pos, train_y, word_num

    def bert_token(self, sents, max_len:int):
        tokens = self.auTokenizer.encode_plus(sents, max_length=max_len,truncation=True, padding='max_length',add_special_tokens=True, return_token_type_ids=False, is_split_into_words=True)
        return tokens['input_ids'], tokens['attention_mask']

    def train(self, input_fn:str, val_fn:str, ep_num:int=100, lstm_layer_num:int=2, save_model:bool=True, USE_BI:bool=False):
        if not self.use_bert:
            word_train, pos_train, y_train, word_num = self.transform_traindata(os.path.join(self.DATA_DIR, input_fn), sh_name='LCQUAD', shuffle=True)
            test_word, test_pos, test_y, word_num = self.transform_traindata(os.path.join(self.DATA_DIR, val_fn), sh_name='LCQUAD-test', shuffle=False)
            model = self.build_model(lstm_layer_num, USE_BILSTM=USE_BI)
            model.fit(
                {"word_input_layer": word_train, "pos_input_layer": pos_train},
                {"crf_layer": y_train},
                validation_data=([test_word, test_pos], test_y),
                batch_size=48,
                shuffle=False,
                epochs=ep_num
            )
        else:
            word_train, word_msk, pos_train, y_train, word_num = self.transform_BERTtraindata(os.path.join(self.DATA_DIR, input_fn), sh_name='LCQUAD', shuffle=True)
            test_word, test_msk, test_pos, test_y, word_num = self.transform_BERTtraindata(os.path.join(self.DATA_DIR, val_fn),sh_name='LCQUAD-test', shuffle=False)
            model = self.build_BERTmodel(lstm_layer_num, USE_BILSTM=USE_BI)
            model.fit(
                {"word_input_layer": word_train, "attention_mask": word_msk, "pos_input_layer": pos_train},
                {"crf_layer": y_train},
                validation_data=([test_word, test_msk, test_pos], test_y),
                batch_size=48,
                shuffle=False,
                epochs=ep_num
            )
        if save_model:
            print('saving model ...')
            max_acc = max(model.history.history['val_get_accuracy'])
            file_name = 'ERC_'+input_fn.replace('.xlsx', '') + str(round(max_acc, 3)) + '_' + str(ep_num) + 'ep_' + str(lstm_layer_num)
            if USE_BI:
                file_name += 'layer_bilstmCRF.h5'
            else:
                file_name += 'layer_lstmCRF.h5'
            if self.use_bert:
                file_name = 'BERT_'+file_name
            model.save('../model/ERC/'+ file_name)
            del model
            return file_name

    def test(self, test_data:str, model_path:str, sh_name:str='', USE_BERT:bool=False):
        model = self.load_model(model_path)
        trans_action = {i: t for t, i in self.erc2idx.items()}
        if not USE_BERT:
            test_word, test_pos, test_y, word_num = self.transform_traindata(os.path.join(self.DATA_DIR, test_data), sh_name=sh_name, shuffle=False)
            seq_pre = model.predict([test_word, test_pos])
        else:
            test_word, test_msk, test_pos, test_y, word_num = self.transform_BERTtraindata(os.path.join(self.DATA_DIR, test_data),sh_name=sh_name, shuffle=False)
            seq_pre = model.predict([test_word, test_msk, test_pos])

        ans = self.logits_to_tokens(test_y, trans_action)
        outcome = self.logits_to_tokens(seq_pre, trans_action)
        print("tag accuracy:", calculate_tag_acc(outcome, ans))

    def logits_to_tokens(self, sequences, index):
        token_sequences = []
        for categorical_sequence in sequences:
            token_sequence = []
            for categorical in categorical_sequence:
                if categorical == 0:
                    continue
                token_sequence.append(index[categorical])

            token_sequences.append(token_sequence)

        return token_sequences

    def build_model(self, lstm_num:int=2, USE_BILSTM:bool=False , unit_num:int=128):
        print('build the model ...')
        # input layer
        word_input = layers.Input(shape=(self.MAX_LENGTH,), dtype='int32', name="word_input_layer")
        pos_input = layers.Input(shape=(self.MAX_LENGTH,), dtype='int32', name="pos_input_layer")

        # 加上mask layer 可以過濾0 的值 <null>
        word_mask = layers.Masking(mask_value=0, name='mask_word')(word_input)
        pos_mask = layers.Masking(mask_value=0, name='mask_pos')(pos_input)
        # embedding layer: word using glove, pos using 丞芸訓練的pos embedding, 其它讓他訓練
        embedded_word = layers.Embedding(len(self.word2idx), self.EMBEDDING_DIM, weights=[np.array(self.wordVectors)],
                                         input_length=(self.MAX_LENGTH), trainable=False)(word_mask)  # trainable=False 使用glove不要訓練

        embedded_pos = layers.Embedding(len(self.pos2idx), 20, weights=[np.array(self.posVectors)],
                                        input_length=(self.MAX_LENGTH), trainable=False)(pos_mask)

        concatenated = layers.Concatenate()([embedded_word, embedded_pos])
        # concatenated = layers.BatchNormalization()(concatenated)

        print(concatenated.shape)

        if USE_BILSTM:
            for i in range(lstm_num):
                if lstm_num == 1:
                    bilstm = layers.Bidirectional(layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True))(
                        concatenated)
                    bilstm = layers.Dropout(0.2)(bilstm)
                else:
                    if i == 0:
                        dense = layers.TimeDistributed(layers.Dense(unit_num*2, kernel_regularizer='l2'))(concatenated)
                    if i == lstm_num - 1:  # 最後一層
                        bilstm = layers.Bidirectional(layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True))(dense)
                        bilstm = layers.Dropout(0.2)(bilstm)
                    else:
                        bilstm = layers.Bidirectional(layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True))(dense)
                        bilstm = layers.Dropout(0.2)(bilstm)
                        # add & norm
                        add2 = layers.Add()([dense, bilstm])
                        dense = LayerNormalization()(add2)
        else:
            for i in range(lstm_num):
                if lstm_num == 1:
                    bilstm = layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True)(concatenated)
                    bilstm = layers.Dropout(0.2)(bilstm)
                else:
                    if i == 0:
                        dense = layers.TimeDistributed(layers.Dense(unit_num, kernel_regularizer='l2'))(concatenated)
                    if i == lstm_num - 1:  # 最後一層
                        bilstm = layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True)(dense)
                        bilstm = layers.Dropout(0.2)(bilstm)
                    else:
                        bilstm = layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True)(dense)
                        bilstm = layers.Dropout(0.2)(bilstm)
                        # add & norm
                        add2 = layers.Add()([dense, bilstm])
                        dense = LayerNormalization()(add2)

        # bilstm = layers.Dense(len(self.actLabel2idx))(bilstm)

        crf_layer = CRF(len(self.erc2idx), name="crf_layer")
        output = crf_layer(bilstm)

        model = Model([word_input, pos_input], output)
        model.compile(loss=crf_layer.get_loss, optimizer=Adam(0.0035), metrics=[crf_layer.get_accuracy])
        model.summary()
        tf.keras.utils.plot_model(model, "ERC_lstm_CRF_model.png", show_shapes=True)
        return model

    def build_BERTmodel(self, lstm_num:int=2, USE_BILSTM:bool=False , unit_num:int=128):
        print('build the model ...')
        bert = TFAutoModel.from_pretrained('bert-base-cased')
        # input layer
        word_input = layers.Input(shape=(self.MAX_LENGTH*2,), dtype='int32', name="word_input_layer")
        word_mask = layers.Input(shape=(self.MAX_LENGTH*2,), name='attention_mask', dtype='int32')
        pos_input = layers.Input(shape=(self.MAX_LENGTH*2,), dtype='int32', name="pos_input_layer")

        # 加上mask layer 可以過濾0 的值 <null>
        pos_mask = layers.Masking(mask_value=0, name='mask_pos')(pos_input)


        embedded_word = bert.bert(word_input, attention_mask=word_mask)[0]

        embedded_pos = layers.Embedding(len(self.pos2idx), 20, weights=[np.array(self.posVectors)], trainable=False)(pos_mask)

        concatenated = layers.Concatenate()([embedded_word, embedded_pos])
        # concatenated = layers.BatchNormalization()(concatenated)

        print(concatenated.shape)

        if USE_BILSTM:
            for i in range(lstm_num):
                if lstm_num == 1:
                    bilstm = layers.Bidirectional(layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True))(
                        concatenated)
                    bilstm = layers.Dropout(0.2)(bilstm)
                else:
                    if i == 0:
                        dense = layers.TimeDistributed(layers.Dense(unit_num*2, kernel_regularizer='l2'))(concatenated)
                    if i == lstm_num - 1:  # 最後一層
                        bilstm = layers.Bidirectional(layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True))(dense)
                        bilstm = layers.Dropout(0.2)(bilstm)
                    else:
                        bilstm = layers.Bidirectional(layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True))(dense)
                        bilstm = layers.Dropout(0.2)(bilstm)
                        # add & norm
                        add2 = layers.Add()([dense, bilstm])
                        dense = LayerNormalization()(add2)
        else:
            for i in range(lstm_num):
                if lstm_num == 1:
                    bilstm = layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True)(concatenated)
                    bilstm = layers.Dropout(0.2)(bilstm)
                else:
                    if i == 0:
                        dense = layers.TimeDistributed(layers.Dense(unit_num, kernel_regularizer='l2'))(concatenated)
                    if i == lstm_num - 1:  # 最後一層
                        bilstm = layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True)(dense)
                        bilstm = layers.Dropout(0.2)(bilstm)
                    else:
                        bilstm = layers.LSTM(unit_num, recurrent_dropout=0.2, return_sequences=True)(dense)
                        bilstm = layers.Dropout(0.2)(bilstm)
                        # add & norm
                        add2 = layers.Add()([dense, bilstm])
                        dense = LayerNormalization()(add2)

        # bilstm = layers.Dense(len(self.actLabel2idx))(bilstm)

        crf_layer = CRF(len(self.erc2idx), name="crf_layer")
        output = crf_layer(bilstm)

        model = Model([word_input, word_mask, pos_input], output)
        model.layers[4].trainable = False
        model.compile(loss=crf_layer.get_loss, optimizer=Adam(0.0035), metrics=[crf_layer.get_accuracy])
        model.summary()
        tf.keras.utils.plot_model(model, "BERT_ERC_lstm_CRF_model.png", show_shapes=True)
        return model

    def load_model(self, fn):
        print('loading model ...')
        path = self.MODEL_DIR +fn
        crf_layer = CRF(len(self.erc2idx))
        model = load_model(path,custom_objects={'CRF': CRF, 'get_loss': crf_layer.get_loss, 'get_accuracy': crf_layer.get_accuracy})
        return model

    def vocab_to_Index(self, vocab_list):
        def file_to_dic(path):
            """
            convert a path into a dic
            """
            res = {}
            file = open(path, 'r', encoding="utf8")
            l = file.readline()
            while l:
                line = l.strip()
                fields = line.split(" ")
                res[fields[0]] = int(fields[1])
                l = file.readline()
            return res

        idx_list = []
        for fn in vocab_list:
            resdict = file_to_dic(os.path.join(self.VOCAB_DIR, fn))
            idx_list.append(resdict)
        return idx_list[:]

    def get_WordEmbedding(self, emb_size):
        wordVectors = [np.zeros(emb_size), np.random.randn(emb_size), np.random.randn(emb_size),
                       np.random.randn(emb_size), np.random.randn(emb_size)]
        glove = 'glove.6B.' + str(emb_size) + 'd.txt'
        glove_file = open(os.path.join(self.GLOVE_DIR, glove), encoding="utf8")
        for line in glove_file:
            word, coefs = line.split(maxsplit=1)
            coefs = np.fromstring(coefs, "f", sep=" ")
            wordVectors.append(coefs)

        glove_file.close()
        return wordVectors

    def get_PosEmbedding(self):
        pos_file = open(os.path.join(self.EMBED_DIR, 'pos_emb_win5_size20_keras_noComma.txt'), encoding="utf8")
        posVectors = [np.zeros(20), np.random.randn(20), np.random.randn(20), np.random.randn(20)]
        for line in pos_file:
            pos, coefs = line.split(maxsplit=1)
            coefs = np.fromstring(coefs, "f", sep=" ")
            posVectors.append(coefs)
        posVectors = np.asarray(posVectors)
        pos_file.close()
        return posVectors
    def set_modelPATH(self,model_path:str):
        self.model_path = model_path





# print('Where can I find things run by the maritime museum of San Diego?')
# erc = ERC_Tagger('Where can I find things run by the maritime museum of San Diego')
# print(erc.predict_erctag())
'''
ERC_TAGGER = ERC_Tagger(use_bert=False)
print('max len:',ERC_TAGGER.MAX_LENGTH)
print(ERC_TAGGER.predictERCtag('Name the movie written by Monty Python and, distributed? by Cinema International Corporation. ?'))
'''
# file_name =  ERC_TAGGER.train('LCQUAD.xlsx', 'LCQUAD.xlsx',250, lstm_layer_num=1, save_model=True,USE_BI=True)#'QALD9train
# ERC_TAGGER.test('LCQUAD.xlsx', model_path='BERT_ERC_LCQUAD0.977_250ep_1layer_bilstmCRF.h5', sh_name='LCQUAD-test', USE_BERT=False)
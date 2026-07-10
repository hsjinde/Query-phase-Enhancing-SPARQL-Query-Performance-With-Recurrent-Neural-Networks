import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import numpy as np
import tensorflow as tf
from tensorflow import keras

class QALD_7():
    def tokenize(sentence):
        from transformers import AutoTokenizer
        maxlen = 20
        tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
        tokens = tokenizer.encode_plus(sentence, max_length=maxlen,
                                       truncation=True, padding='max_length',
                                       add_special_tokens=True, return_attention_mask=True,
                                       return_token_type_ids=False, return_tensors='tf')
        return tokens['input_ids'], tokens['attention_mask']
    
    def classifiers():
        from transformers import TFAutoModel
        bert = TFAutoModel.from_pretrained('bert-base-cased')
        classifiers = []
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer2_0.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_1.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_2.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_3.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer2_4.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_5.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_6.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_7.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_8.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_9.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_10.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_11.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/QALD-7/Bert_QALD-7_Layer1_12.h5", custom_objects={"TFBertModel": bert}, compile = False))
        return classifiers
    
    def predict(classifiers, test_dataset):
        result = np.zeros((1, len(classifiers)))
        for i in range(len(classifiers)):
            result[0][i] = classifiers[i].predict(test_dataset)
        return result

class LCQUAD():
    def tokenize(sentence):
        from transformers import AutoTokenizer
        maxlen = 30
        tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
        tokens = tokenizer.encode_plus(sentence, max_length=maxlen,
                                       truncation=True, padding='max_length',
                                       add_special_tokens=True, return_attention_mask=True,
                                       return_token_type_ids=False, return_tensors='tf')
        return tokens['input_ids'], tokens['attention_mask']
    
    def classifiers():
        from transformers import TFAutoModel
        bert = TFAutoModel.from_pretrained('bert-base-cased')
        classifiers = []
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer1_0.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer2_1.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer1_2.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer1_3.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer3_4.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer2_5.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer1_6.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer2_7.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer1_8.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer1_9.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer2_10.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer1_11.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer1_12.h5", custom_objects={"TFBertModel": bert}, compile = False))
        classifiers.append(keras.models.load_model("./model/LCQUAD/Bert_LCQUAD_layer3_13.h5", custom_objects={"TFBertModel": bert}, compile = False))
        return classifiers
    
    def predict(classifiers, test_dataset):
        result = np.zeros((1, len(classifiers)))
        for i in range(len(classifiers)):
            result[0][i] = classifiers[i].predict(test_dataset)
        return result
    
    
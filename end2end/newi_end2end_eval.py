import pandas as pd
import difflib

end2end = pd.read_excel( "LCQUADendtoend_2022.11.2.xlsx")

def caculate(ans, pre):
    correct_num = 0

    if pre == [] or ans == []:
        return 0
    else:
        for a in ans:
            if a in pre:
                correct_num += 1
                continue
            else:
                if 'http' in a:
                    if 'XMLSchema#' in a:
                        a = a.split('http')[0]
                    else:
                        a = a.split('/')[-1]
                for p in pre:
                    if a in p:
                        correct_num += 1
                        find = True
                        break
                    else:
                        if 'http' in p:
                            if 'XMLSchema#' in p:
                                p = p.split('http')[0]
                            else:
                                p = p.split('/')[-1]
                        seq = difflib.SequenceMatcher(lambda x: x in ' _,', a.lower(), p.lower())
                        ratio = seq.ratio()

                        if ratio > 0.9:
                            correct_num += 1
                            find = True
                            break
    return correct_num


class EndToEnd_Evaluator:

    def __init__(self, end2end):
        '''
        if type(predict_path) == pd.core.frame.DataFrame:
            pre_df = predict_path
            self.ref_ans = [ans_path]
            self.enalall = False
        else:
            ans_df = pd.read_excel(ans_path)
            pre_df = pd.read_excel(predict_path, sheet_name=sheet_name)
            self.ref_ans = ans_df['Answer']
            self.enalall = True
'''
 

        self.ref_ans = end2end['true answer']
        #self.pre_ans = end2end['system after Q type']
        self.pre_ans = end2end['system answer']


        self.precision = []
        self.recall = []
        self.f1 = []
        
        self.performace = []


    def evaluation(self):
        num_sent = 0
        for i in range(len(self.ref_ans)):
            #print(type(self.ref_ans[i]))
            self.ref_ans[i] = str( self.ref_ans[i])
            
            # if not i == 961:
            #     continue
            print('\ni=', i)
            # print(type(self.ref_ans[i]))
            # print('ans:',self.ref_ans[i])
            if self.ref_ans[i] == 'Unapplicable':
                continue
            elif type(self.ref_ans[i]) == bool:
                if self.ans_type[i] == 'Number' and self.ref_ans[i] == False:
                    ans = ['0']
                else:
                    ans = [str(self.ref_ans[i])]
            elif type(self.ref_ans[i]) == int:
                ans = [str(self.ref_ans[i])]

            elif ']' in self.ref_ans[i] and '[' in self.ref_ans[i]:
                ans = self.ref_ans[i].split(']')[0].replace("'", '').replace('[', '').strip().split(', ')
            else:
                if self.ref_ans[i].strip()[-1] == '@':
                    ans = self.ref_ans[i].strip().split('@')[:-1]
                else:
                    ans = self.ref_ans[i].strip().split('@')
                # print('!ans:', self.ref_ans[i])
                # print('!ans:', ans)

            print(self.pre_ans[i])
            if str(self.pre_ans[i]) == 'nan' or self.pre_ans[i] == '':
                pre = []
            else:
                #pre = str(self.pre_ans[i]).split('@')
                pre = self.pre_ans[i].split(']')[0].replace("'", '').replace('[', '').strip().split(', ')
                
            num_sent +=1
            correct_num = 0
            num_ans = len(ans)
            num_pre = len(pre)


            print('len ans:', len(ans))
            if not num_ans > 100:
                print('ans:', ans)
            else:
                print('ans num > 100')
            print('len pre:', len(pre))
            if not num_pre > 100:
                print('pre:', pre)
            else:
                print('pre ans num > 100')

            if pre == [] or ans == []:
                self.precision.append(0.0)
                self.recall.append(0.0)
                self.f1.append(0.0)
                print('\nprecision:', str(0.0))
                print('recall:', str(0.0))
                print('f1:', str(0.0))
            else:
                for a in ans:
                    if a == '' or a == None:
                        num_ans -= 1
                        continue
                    if a in pre:
                        correct_num += 1
                        continue
                    else:
                        if 'http' in a:
                            if 'XMLSchema#' in a:
                                a = a.split('http')[0]
                            else:
                                if 'http:' in a and not 'http://dbpedia.org' in a:
                                    num_ans -= 1
                                    continue
                                else:
                                    a = a.split('/')[-1]
                        for p in pre:
                            if p == '' or p == None:
                                num_pre -= 1
                                continue
                            if a.lower() in p.lower():
                                correct_num += 1
                                find = True
                                break
                            else:
                                if 'http' in p:
                                    if 'XMLSchema#' in p:
                                        p = p.split('http')[0]
                                    else:
                                        if not 'http://dbpedia.org' in p:
                                            num_pre -= 1
                                            continue
                                        else:
                                            p = p.split('/')[-1]
                                seq = difflib.SequenceMatcher(lambda x: x in ' _,', a.lower(), p.lower())
                                ratio = seq.ratio()

                                if ratio > 0.9:
                                    correct_num += 1
                                    find = True
                                    # print('\n- find similar ratio -')
                                    # print('a:', a)
                                    # print('p:', p)
                                    # print('ratio:', ratio)
                                    break

                if correct_num == 0:
                    precision = 0.0
                    recall = 0.0
                    f1 = 0.0
                    self.precision.append(0.0)
                    self.recall.append(0.0)
                    self.f1.append(0.0)
                else:
                    precision = correct_num/num_pre
                    recall = correct_num/num_ans
                    f1 = (2*precision*recall)/(precision+recall)
                    self.precision.append(precision)
                    self.recall.append(recall)
                    self.f1.append(f1)
                print('\nCorrect Num:', correct_num)
                print('precision:', precision)
                print('recall:', recall)
                print('f1:', f1)
            self.performace.append([precision, recall, f1])
            pd.DataFrame(self.performace, columns=['precision', 'recall','f1']).to_excel('eenndd_an.xlsx')
        if num_sent == 0:
            result = {'Precision': 0.0,
                      'Recall': 0.0,
                      'F1-measure': 0.0}
        else:
            result = {'Precision': sum(self.precision) / num_sent,
                      'Recall': sum(self.recall) / num_sent,
                      'F1-measure': sum(self.f1) / num_sent}
        print('\nEval Sentence Number:', num_sent)
        print(result)
        return result









# ee = EndToEnd_Evaluator('../output/correct_ans/LCQUAD-test.xlsx', '../output/ans_output/QALDend2end - LCQUAD.xlsx',sheet_name='Bert-LCQUAD-test') # Bert-LCQUAD-test  Glove-QALD8
# result = ee.evaluation()



#
# ee = EndToEnd_Evaluator('../output/correct_ans/QALD-7.xlsx', '../output/ans_output/QALDend2end.xlsx',sheet_name='Glove-QALD7')
# result = ee.evaluation()

# ff = './新文字文件.txt'
#
# with open(ff, 'r', encoding="utf-8") as f:
#     all_t = f.read()
#     list_s = all_t.replace('\n', '').strip().split(',')
#     print(list_s)

#from src.DBpediaQueries import DBpediaQueries
# db = DBpediaQueries()
# q9 = pd.read_excel('../output/correct_ans/QALD-8.xlsx')
# result_list = []
# for i, row in q9.iterrows():
#     if 'ask where' in row['query'].lower():
#         # print(row['query'].replace('"', '').replace('\n', '').strip())
#         result = db.executeSparqlASK(row['query'].replace('"', '').replace('\n', '').split('{')[1].replace('}', '').strip())
#     else:
#         result = db.executeSparqlSearch(row['query'].replace('"', '').replace('\n', '').strip())
#     result_list.append(str(result))
#
# ans_result = {"Answer": result_list}
# pd.DataFrame(ans_result).to_excel('../output/correct_ans/QALD-8ans.xlsx')
#
# db = DBpediaQueries()
# result = db.executeSparqlSearch('SELECT DISTINCT ?date WHERE {  dbr:Finland dbp:establishedDate ?date }')
# print(result)
# result = db.executeSparqlASK('<http://dbpedia.org/resource/Peter_Piper_Pizza> <http://dbpedia.org/ontology/industry> <http://dbpedia.org/resource/Pizza> . ')
# print(result)
import pandas as pd
import difflib


end2end = pd.read_excel( "LCQUADendtoend.xlsx")


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

global performace  

class EndToEnd_Evaluator:

    def __init__(self, end2end):
        #ans_df = pd.read_excel(ans_path)
        #pre_df = pd.read_excel(predict_path, sheet_name=sheet_name)

        self.ref_ans = end2end['true answer']
        self.pre_ans = end2end['system after Q type']

        self.precision = []
        self.recall = []
        self.f1 = []
        
        self.performace = []

    def evaluation(self):
        for i in range(len(self.ref_ans)):
            self.ref_ans[i] = str( self.ref_ans[i])
            ans = self.ref_ans[i].split(']')[0].replace("'", '').replace('[', '').strip().split(', ')
            if str(self.pre_ans[i]) == 'nan' or self.pre_ans[i] == '':
                pre = []
            else:
                pre = self.pre_ans[i].split('◎')

            correct_num = 0
            num_ans = len(ans)
            num_pre = len(pre)

            print('\ni=', i)
            print('len ans:', len(ans))
            print('ans:', ans)
            print('len pre:', len(pre))
            print('pre:', pre)
            if pre == [] or ans == []:
                precision = recall = f1 = 0.0
                self.precision.append(0.0)
                self.recall.append(0.0)
                self.f1.append(0.0)
                print('\nprecision:', str(0.0))
                print('recall:', str(0.0))
                print('f1:', str(0.0))
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
            pd.DataFrame(self.performace, columns=['precision', 'recall','f1']).to_excel('eenndd.xlsx')
        n = len(self.precision) or 1   # number of questions actually scored
        result = {'Precision': sum(self.precision) / n,
                  'Recall': sum(self.recall) / n,
                  'F1-Measure': sum(self.f1) / n}
        
        
        
        print(result)
        return result

#self.performace.append([precision,recall,f1])
#pd.DataFrame(self.performace, columns=['precision', 'recall','f1']).to_excel('eenndd.xlsx')







# ee = EndToEnd_Evaluator('../output/correct_ans/QALD-8.xlsx', '../output/ans_output/QALDend2end.xlsx',sheet_name='Glove-QALD8')
# result = ee.evaluation()



#
# ee = EndToEnd_Evaluator('../output/correct_ans/QALD-8.xlsx', '../output/ans_output/QALDend2end.xlsx',sheet_name='Glove-QALD8')
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
def combineEntity_Tag(word_tag):
    # 將tag轉成數字的dictionary。
    # 每個角色 (V/R/E/C/...) 佔一段連號:B/I/E 依序 +0/+1/+2,角色之間留一個空號
    # (例如 V-B=0..V-E=2,下一個 R-B 從 4 開始)。這樣「相鄰數字差 1」就代表
    # 「同一個 entity 的下一個 B/I/E」,下面的合併邏輯與 ilist 都靠這個編碼運作。
    tag_dic = {"V-B": 0, "V-I": 1, "V-E": 2, "R-B": 4, "R-I": 5, "R-E": 6, "E-B": 8,
               "E-I": 9, "E-E": 10, "C-B": 12, "C-I": 13, "C-E": 14, "N": 16, "CR-B": 18, "CR-I": 19, "CE-B": 21, "CE-I": 22, "ER-B": 24, "ER-I": 25, "VR-B": 27, "VR-I": 28,
               "RR-B":30, "RR-I":31, "L-B":33, "L-I":34}
    # 將數字轉回tag的dictionary
    num_dic = {0: "V-B", 1: "V-I", 2: "V-E", 4: "R-B", 5: "R-I", 6: "R-E", 8: "E-B",
               9: "E-I", 10: "E-E", 12: "C-B", 13: "C-I", 14: "C-E", 16: "N", 18: "CR-B", 19: "CR-I", 21: "CE-B", 22: "CE-I", 24: "ER-B", 25: "ER-I", 27: "VR-B", 28: "VR-I",
               30:"RR-B", 31: "RR-I", 33:"L-B", 34:"L-I"}
    tagg = []
    combineText = ""
    combineTag = ""

    for i, element in enumerate(word_tag):
        # 未知標記(例如 tagger 偶發吐出組合標記的 -E 變體 'ER-E',或 'O')
        # 一律當作非實體 'N' 處理,避免 KeyError 中斷整條 pipeline。
        tagg.append(tag_dic.get(word_tag[i], tag_dic["N"]))

    # 單一 token(或空)問句不會進入下面的成對 while 迴圈,否則 combineTag 會是空字串、
    # 導致下游斷詞錯誤。直接回傳單一 tag 與字數 1。
    if len(tagg) <= 1:
        if len(tagg) == 1:
            return num_dic[tagg[0]], [1]
        return "", []

    n_arr = []
    j = 0
    n = 0 #計算每個entity單字數
    ilist = [1, 5, 9, 13, 19, 22, 25, 28, 31, 34]
    while j < len(tagg)-1:
        # 下一個單字的index
        # 讀到第一個單字直接加到字串中
        if j == 0:
            combineTag += num_dic[tagg[j]]
            n += 1

        # tag為1,5,9,13代表tag結尾是 -I
        if tagg[j] in ilist:
            if (tagg[j + 1] - tagg[j]) == 1 or (tagg[j + 1] - tagg[j]) == 0:   # 與後一個tag相差1代表後面tag結尾是 -E,
                # 與後一個tag相差0代表後面tag結尾一樣是 -I
                combineTag += " " + num_dic[tagg[j + 1]]
                n += 1
            else:   # 其他情形代表後面tag是不同entity加斜線
                combineTag += "/"+num_dic[tagg[j + 1]]
                n_arr.append(n)
                n = 1
        else:
            if (tagg[j + 1] - tagg[j]) == 1:    # 與後一個tag相差1代表後面tag結尾是 -I
                combineTag += " " + num_dic[tagg[j + 1]]
                n += 1
            else:                           # 其他情形代表後面tag是不同entity加斜線
                combineTag += "/"+num_dic[tagg[j + 1]]
                n_arr.append(n)
                n = 1
        j += 1
    n_arr.append(n)
    #print("comTag: ",combineTag)
    return combineTag,n_arr

def tag_acc(predict,y):
    correct_count = 0
    n = 0
    # print(len(y))
    # print(len(predict))
    # 複製一份再補齊,避免就地修改呼叫端傳入的 predict(副作用)。
    predict = list(predict)
    if len(y)>len(predict):
        x = len(y) - len(predict)
        for _ in range(x):
            predict.append('N')
    # print(y)
    # print(predict)
    y_sent,num_arr = combineEntity_Tag(y)
    y_ent_arr = y_sent.split('/')
    for i in range(len(y_ent_arr)):
        s = ""
        for j in range(num_arr[i]):
            if j == 0:
                s += predict[n+j]
            else:
                s += " "+predict[n+j]            
        n += num_arr[i]
        
        if s == y_ent_arr[i]:
            correct_count += 1
            print("word: ",s+" (o)")
            print("y: ",y_ent_arr[i])
        else:
            print("word: ",s+" (X)")
            print("y: ",y_ent_arr[i])
    acc = float(correct_count/len(y_ent_arr))
    print("Correct/ALL",correct_count,"/",len(y_ent_arr))
    print("\n")
    return acc

def calculate_tag_acc(pre,y):
    score = 0
    for i in range(len(pre)):
        print("i= ",i)
        score += tag_acc(pre[i], y[i])
    accuracy = score/len(pre)
    return accuracy

'''
text = [['V-B', 'E-B', 'N', 'E-B', 'N', 'N', 'E-B', 'N'],['V-B', 'N', 'E-B', 'E-I', 'R-B', 'N', 'N', 'E-B', 'N', 'N', 'N'],['V-B', 'V-I', 'R-B', 'N', 'E-B', 'N', 'N', 'E-B', 'N'],['V-B', 'V-I', 'E-B', 'N', 'N', 'E-B'],['V-B', 'V-B', 'R-B', 'N', 'E-B', 'E-I', 'N', 'N', 'N'],['V-B', 'E-B', 'R-B', 'N', 'E-B'],['V-B', 'E-B', 'R-B', 'N', 'E-B'],['V-B', 'E-B', 'R-B', 'R-B'],['V-B', 'R-B', 'R-I', 'R-E', 'N', 'E-B', 'N', 'E-B', 'N'],['V-B', 'N', 'N', 'R-B', 'R-I', 'N'],['V-B', 'N', 'E-B', 'R-B'],['V-B', 'N', 'N', 'E-B', 'E-I', 'R-B', 'R-B'],['V-B', 'N', 'E-B', 'E-I', 'R-B'],['V-B', 'V-B', 'N', 'E-B', 'R-B', 'N', 'E-B'],['V-B', 'R-B', 'R-B'],['V-B', 'N', 'R-B', 'N', 'N', 'E-B', 'E-I', 'N', 'N'],['V-B', 'R-B', 'N', 'E-B', 'E-I'],['V-B', 'N', 'E-B', 'R-B', 'N', 'N'],['V-B', 'V-I', 'R-B', 'N', 'N', 'E-B'],['V-B', 'N', 'N', 'C-B', 'R-I', 'N', 'N'],['V-B', 'N', 'N', 'R-B', 'R-I', 'R-E', 'N', 'E-B', 'E-I', 'N', 'N', 'N', 'E-I'],['V-B', 'N', 'N', 'C-B', 'R-I', 'R-E', 'E-B', 'N'],['V-B', 'V-B', 'N', 'E-B', 'R-B', 'R-B']]
y = [['V-B', 'E-B', 'N', 'E-B', 'N', 'N', 'R-B', 'R-I'],['V-B', 'N', 'E-B', 'E-I', 'E-E', 'N', 'N', 'R-B', 'R-I', 'R-E', 'E-B'],['V-B', 'V-I', 'C-B', 'N', 'C-B', 'N', 'N', 'E-B', 'E-I'],['V-B', 'V-I', 'C-B', 'N', 'N', 'C-B'],['V-B', 'V-I', 'C-B', 'N', 'E-B', 'E-I', 'R-B', 'R-I', 'R-E'],['V-B', 'E-B', 'E-I', 'N', 'C-B'],['V-B', 'E-B', 'N', 'N', 'C-B'],['V-B', 'E-B', 'E-I', 'R-B'],['V-B', 'R-B', 'R-I', 'R-E', 'N', 'N', 'N', 'E-B', 'E-I'],['V-B', 'N', 'N', 'R-B', 'R-I', 'E-B'],['V-B', 'N', 'E-B', 'R-B'],['V-B', 'N', 'N', 'E-B', 'E-I', 'N', 'R-B'],['V-B', 'N', 'E-B', 'E-I', 'R-B'],['V-B', 'C-B', 'N', 'N', 'N', 'N', 'N'],['V-B', 'R-B', 'E-B'],['V-B', 'N', 'R-B', 'R-I', 'N', 'E-B', 'E-I', 'E-I', 'E-E'],['V-B', 'R-B', 'N', 'E-B', 'E-I'],['V-B', 'N', 'E-B', 'R-B', 'N', 'N'],['V-B', 'V-I', 'R-B', 'N', 'N', 'E-B'],['V-B', 'N', 'N', 'R-B', 'R-I', 'E-B', 'E-I'],['V-B', 'N', 'N', 'R-B', 'R-I', 'R-I', 'N', 'N', 'E-B', 'E-I', 'E-I', 'E-I', 'E-E'],['V-B', 'N', 'N', 'R-B', 'R-I', 'R-E', 'E-B', 'E-I'],['V-B', 'C-B', 'N', 'E-B', 'E-I', 'R-B']]

print("Accuracy: ", calculate_tag_acc(text, y))
'''
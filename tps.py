import random
import matplotlib.pyplot as plt
import pandas as pd
import math
import copy
import csv

#-----使用する変数の宣言-----
generation = 1000                               #世代数
dimension = 38                                  #街の数
p = 200                                         #親の数
p_index = [i for i in range(p)]                 #parentsの添え字
parents = [0] * p                               #親を管理する配列
children = [[] for i in range(p)]               #子を管理する配列
total_fitness = 0                               #適合度の合計
fitness = [0] * p                               #適合度を管理する配列
fitness_max_index = 0                           #適合度が最も高い親の添え字を格納
x_data = [0 for i in range(dimension)]          #グラフの描画に使用
y_data = [0 for i in range(dimension)]          #グラフの描画に使用
el = 100                                         #引き継ぐ個体の数を指定する(偶数指定)
adjacency_list = [[] for i in range(dimension)] #隣接リストの作成
CX = []                                         #子生成のために親から選ばれた巡回路１
CY = []                                         #子生成のために親から選ばれた巡回路２
cx = [0 for i in range(dimension)]              #生成した子を一次的に格納
cy = [0 for i in range(dimension)]              #生成した子を一次的に格納
LX = []
LY = []
Lx = []
Ly = []
D = [0 for i in range(dimension)]               #教科書のD
c = 0                                           #教科書のc*の役割
number = 0                                      #教科書のiの役割
min = 0                                         #min|A|に使う
k_star = []                                     #教科書のk*の役割
unvisited = [i for i in range(dimension)]       #未訪問の都市
array1_tmp = []
array2_tmp = []
cross_over_prob = 0.80                          #交叉の起こる確率
mutation_prob = 0.05                            #突然変異の起こる確率
old_fitness = 0                                 #
distance = [[0]*dimension for i in range(dimension)]
# aaa = 0           #各世代の最適合度
# average = 0         #各世代の平均値
#---------------------------

#-----適合度を計算-----
def cal_fitness(parents):
    global total_fitness
    total_fitness = 0
    global fitness
    fitness = [0] * p
    for i in range(p):
        for j in range(dimension-1):
            fitness[i] = fitness[i] + distance[parents[i][j]][parents[i][j+1]]
        fitness[i] = fitness[i] + distance[parents[i][0]][parents[i][dimension-1]]
        
        total_fitness = total_fitness + fitness[i]
#---------------------

#-----適合度の順に並び替え-----
def sort():
    global sorted_fitness
    global sorted_p_index
    global fitness_max_index
    # 適合度でソート
    sorted_p_index = sorted(zip(fitness, p_index), key=lambda x: x[0])

    # ソート後の適合度と親のリストを分離                  #fitness=[32, 56, 21, 78, 93]
    sorted_fitness = [x[0] for x in sorted_p_index]     #fitnessを昇順に並び替え[21, 32, 56, 78, 93]
    sorted_p_index = [x[1] for x in sorted_p_index]     #その時の親の添え字を保存[2, 0, 1, 3, 4]

    fitness_max_index = sorted_p_index[0]
#-----------------------------

#-----エリート戦略-----
def elite(el):
    global children
    for i in range(el):
        children[i] = parents[sorted_p_index[i]]     #子供に適合度の高い順に引き継ぐ
#----------------------

#-----ルーレット方式(世代1からは最適な個体が選ばれやすいようにする)-----
def roulette():
    fitness_score = [1/i for i in fitness]
    total_fitness_score = 0
    num = 0
    for j in fitness_score:
        total_fitness_score = total_fitness_score + j                                     
    selection_prpbability = [k/total_fitness_score for k in fitness_score]
    rand = random.random()
    for l in range(len(selection_prpbability)):
        num = num + selection_prpbability[l]
        if(rand <= num):
            return parents[l]
#-----------------------------------------------------

#-----隣接リストを作る-----
#この関数は選ばれたそれぞれの親が呼び出し、自身の隣接リストを作成する
def create_list(parents1, parents2):
    global list
    list = [[] for i in range(dimension)]
    global adjacency_list
    adjacency_list = [[] for i in range(dimension)]
    create_adjacency_list(parents1)
    create_adjacency_list(parents2)

def create_adjacency_list(parents):
    for i in range(dimension):
        if( i == 0):
            list[parents[i]].append(parents[dimension-1])   #始点は一つ隣の点と終点と繋がっている
        else:                                               #
            list[parents[i]].append(parents[i-1])           #各点はその前後の点と繋がっている
        if( i+1 == dimension):
            list[parents[i]].append(parents[0])             #始点は一つ隣の点と終点と繋がっている
        else:                                               #
            list[parents[i]].append(parents[i+1])           #各点はその前後の点と繋がっている
    #listの中に重複があるのでそれを削除する
    for j in range(dimension):                              #地点の数分繰り返す
        for k in range(len(list[j])):                       #その地点のlistの数分繰り返す
            if list[j][k] not in adjacency_list[j]:         #もし隣接リストに同じ地点が入ってなければ
                adjacency_list[j].append(list[j][k])        #隣接リストに追加する
#---------------------------------------------------------------

#-----隣接リストから該当するものを削除する---
def deleate(c):
    for i in range(dimension):                              #地点の数分繰り返す
        if(c in adjacency_list[i]):
            adjacency_list[i].remove(c)
#------------------------------------------

#-----EX_algorithm-----
def EX_algorithm(C):
    #--step0--
    D = [0 for i in range(dimension)]
    global number
    number = 0
    cc = [0 for i in range(dimension)]
    unvisited = [i for i in range(dimension)]
    cc[0] = C[0]
    D[0] = cc[0]

    while(True):
        #--step1--
        c = cc[number]
        deleate(c)                                          #
        unvisited[c] = '済'                                 #未訪問リストにおいて、訪問したものは'済'にする
        #--step2--
        k_star = []                                         #kを初期化
        if(len(adjacency_list[c]) != 0):                    #もしcの隣接リストが空でないなら
            min = len(adjacency_list[adjacency_list[c][0]]) #隣接リスト最初の要素の長さを最小値とする
            k_star.append(adjacency_list[c][0])             #その時の都市を格納
            for i in adjacency_list[c][1:]:                 #隣接リストの中身について最初を除いて繰り返す
                if(len(adjacency_list[i]) < min):           #もし現在の最小値より小さいなら
                    min = len(adjacency_list[i])            #最小値を更新し
                    k_star = []                             #kを初期化して
                    k_star.append(i)                        #その時の都市を格納
                elif(len(adjacency_list[i]) == min):        #もし現在の最小値と同じなら
                    k_star.append(i)                        #
            
            if(len(k_star) >= 2):                           #もしk*の候補が複数あるなら
                rand = random.randint(0, len(k_star)-1)     #ランダムに選ぶ
                tmp = k_star[rand]
                k_star = []
                k_star.append(tmp)

        else:                                               #もしcの隣接リストが空なら
            for i in unvisited:
                if(i != '済'):                              #もし要素iが'済'ではないなら
                    min = len(adjacency_list[i])            #未訪問都市リストの最初の要素の隣接リストの長さを最小とする
                    k_star.append(i)                        #その時の都市を格納
                    break

            for j in unvisited:
                if((j != '済') & (j != k_star[0])):
                    if(len(adjacency_list[j]) < min):       #もし現在の最小値より小さいなら
                        min = len(adjacency_list[j])        #最小値を更新し
                        k_star = []                         #kを初期化して
                        k_star.append(j)                    #その時の都市を格納
                    elif(len(adjacency_list[j]) == min):    #もし現在の最小値と同じなら
                        k_star.append(j)                    #
            
            if(len(k_star) >= 2):                           #もしk*の候補が複数あるなら
                rand = random.randint(0, len(k_star)-1)     #ランダムに選ぶ
                tmp = k_star[rand]
                k_star = []
                k_star.append(tmp)
        #--step3--
        cc[number+1] = k_star[0]
        D[number+1] = k_star[0]
        number = number + 1
        if(number == dimension-1):                          #もしnumber == dimension-1なら
            return cc                                       #繰り返しを終え、step4へ
#--------------------------

#-----交叉-----
def crossing_over():
    global LX
    global LY

    array1_tmp = []
    array2_tmp = []

    rand = random.randint(1, dimension-1) #ランダムに交差点を決定

    array1_tmp.extend(LY[:rand])
    array1_tmp.extend(LX[rand:])
    array2_tmp.extend(LX[:rand])
    array2_tmp.extend(LY[rand:])

    LX = copy.deepcopy(array1_tmp)
    LY = copy.deepcopy(array2_tmp)
#-----------------------

#-----各ビットを確率で変位させる-----
def Mutation(array):
    global LX
    global LY

    rand_1 = random.randint(0, len(array)-1)
    rand_2 = random.randint(0, len(array)-1)
    swap = array[rand_1]
    array[rand_1] = array[rand_2]
    array[rand_2] = swap

    return array
#-----------------------------------

#-----あらかじめ全ての距離を計算-----
def dist():
    global distance
    for i in range(len(x)):
        for j in range(len(y)):
            distance[i][j] = math.sqrt((x[j]-x[i])**2 + (y[j]-y[i])**2)


#-----
print("start")
#-----

#-----csvファイルからデータの読み込み-----
df = pd.read_csv('data.csv')
x = df['X座標']
y = df['Y座標']
n = [i for i in range(dimension)]

dist()

#-----generation0-----
for i in range (p):                         #-----初期個体の生成-----
   parents[i] = random.sample(n, 38)
cal_fitness(parents)                        #-----適合度を計算-----
sort()                                      #親について適合度の昇順にソート
old_fitness = sorted_fitness[0]             #初期のもっともよい適合度を保存
#--グラフ描画--
fig, ax = plt.subplots()
point, = plt.plot(x, y, 'o')
for i in range(dimension):
    x_data[i] = x[parents[fitness_max_index][i]]
    y_data[i] = y[parents[fitness_max_index][i]]
x_data.append(x[parents[fitness_max_index][0]])
y_data.append(y[parents[fitness_max_index][0]])

line, = ax.plot(x_data, y_data, color='black')
plt.pause(0.000001)
#---------------------


#-----generatin1 ~ generationまで繰り返す-----
for g in range(generation): 

    children = [[] for i in range(p)]

    if(g >= (generation/2)):
        el = 150
        mutation_prob = 1.0
    elite(el)                                   #優秀な個体を次の世代に引き継ぐ

    # if(g > (generation/2)):
    #     mutation_prob = 0.8
    for a in range(0, p, 2):
        LX = []
        LY = []
        Lx = []
        Ly = []
        if(len(children[a]) == 0):
            #-----子を生成するために親を２つ選ぶ-----
            CX = roulette()
            CY = roulette()
            #-----アルゴリズムに従って子を生成する----
            create_list(CX, CY)
            cx = EX_algorithm(CX)               #cxを生成
            create_list(CX, CY)
            cy = EX_algorithm(CY)               #cyを生成

            #-----交叉、突然変異のために形を変える-----
            n = [i for i in range(dimension)]
            LX = [0 for i in range(dimension)]
            LY = [0 for i in range(dimension)]
            for i in range(len(cx)):
                for j in range(0, len(n)):
                    if(cx[i] == n[j]):
                        LX[i] = j
                        n.remove(n[j])
                        break
            n = [i for i in range(dimension)]
            for i in range(len(cy)):
                for j in range(0, len(n)):
                    if(cy[i] == n[j]):
                        LY[i] = j
                        n.remove(n[j])
                        break

            #--確率でランダムに交叉--
            rand = random.random()
            if(rand <= cross_over_prob):
                crossing_over()

            #-----形を戻す-----
            Lx = [0 for i in range(dimension)]
            Ly = [0 for i in range(dimension)]
            n = [i for i in range(dimension)]
            for i in range(len(LX)):
                Lx[i] = n[LX[i]]
                n.remove(n[LX[i]])
            n = [i for i in range(dimension)]
            for i in range(len(LY)):
                Ly[i] = n[LY[i]]
                n.remove(n[LY[i]])

            #--確率で突然変異させる--
            rand = random.random()
            if(rand <= mutation_prob ):
                Lx = copy.deepcopy(Mutation(Lx))
            rand = random.random()
            if(rand <= mutation_prob ):
                Ly = copy.deepcopy(Mutation(Ly))

            children[a] = copy.deepcopy(Lx)                    #生成した子を保存
            children[a+1] = copy.deepcopy(Ly)                  #生成した子を保存

    cal_fitness(children)
    parents = copy.deepcopy(children)
    sort()                                      #親について適合度の昇順にソート

    # #-----csvに出力（各世代の最良解と平均値）-----
    # aaa = sorted_fitness[0]
    # average = total_fitness / p
    # with open('b.csv', 'a') as f:
    #     print('{},{}'.format(aaa,average),file=f)
    # #--------------------------------------------

    #-----グラフ描画-----
    if(sorted_fitness[0] < old_fitness):
        old_fitness = sorted_fitness[0]
        line.remove()
        x_data = [0 for i in range(dimension)]
        y_data = [0 for i in range(dimension)]
        for i in range(dimension):
            x_data[i] = x[children[fitness_max_index][i]]
            y_data[i] = y[children[fitness_max_index][i]]
        x_data.append(x[children[fitness_max_index][0]])
        y_data.append(y[children[fitness_max_index][0]])
        
        line, = ax.plot(x_data, y_data, color='black')
        plt.pause(0.000001)
    #------------------

print("sorted_fitness", sorted_fitness[0])

print("Enterキーを押すと終了します")
input_data = input()
print("終了します")
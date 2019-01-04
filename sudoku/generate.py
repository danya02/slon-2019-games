# coding:utf-8
import random
#random.seed(0)
n = 6
l = 3
k = 2
while n != k * l:
    l = int(input('l = '))
    k = int(input('k = '))
main_array = [[0 for i in range(n)] for i in range(n)]
def stolb(y0, x0):#проверка столба
    for y in range(n):
        if main_array[y][x0] == main_array[y0][x0] and y != y0:
            return False
    return True
def stroka(y0, x0):#проверка строки
    for x in range(n):
        if main_array[y0][x] == main_array[y0][x0] and x != x0:
            return False
    return True
def blok(y0, x0):#проверка блока
    for x in range((x0 // l) * l, (x0 // l + 1) * l):
        for y in range((y0 // k) * k, (y0 // k + 1) * k):
            if y != y0 and x != x0 and main_array[y][x] == main_array[y0][x0]:
                return False
    return True
def shuffledrange(*args):
    a = list(range(*args))
    random.shuffle(a)
    return a
para = [(i, j) for i in range(n) for j in range(n)]
random.shuffle(para)
def check(i, j):
    if stolb(i, j) and stroka(i, j) and blok(i, j):
        return True
    else:
        return False
def generator(r):
    print(r,'   ','\r',flush=True,end='')
    global generator_run
    if r == n ** 2:
        return True
    x = para[r][0]
    y = para[r][1]
    #print(r, x, y)
    generator_run += 1
    for i in range(1, 1 + n):
        main_array[x][y] = i
        #print_array()
        if check(x, y):
            if generator(r + 1):
                return True
    main_array[x][y] = 0
    return False

def print_array():
    for y in range(len(main_array)):
        for x in range(len(main_array[y])):
            print(main_array[y][x], end=' ')
            if (x + 1) % l == 0:
                print('|', end=' ')
        if (y + 1) % k == 0:
            print()
            for i in range(n + int(n / l)):
                print('-', end=' ')
        print()
    print()
    #tyr = input()

generator_run = 0
generator(0)
print_array()

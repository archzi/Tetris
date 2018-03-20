# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 17:13:10 2018

@author: ljd19
"""

'''
俄罗斯方块游戏：
首先游戏有方块有7种；


'''

# 用到的模块

import random,copy
import pygame as pg
from pygame.locals import *

'''
常量声明 
'''
EMPTY_CELL = 0  # 空区标识，表示没有方块
FALLING_BLOCK = 1 # 下落中的方块，也就是活动方块
STATIC_BLOCK = 2 # 固始方块

'''
变量声明
'''
#关于pygame的变量
defaultFont=None        #默认字体
screen=None     # 屏幕输出对象
backSurface=None        #图像输出缓冲画板

score=0     # 玩家得分记录
clearLineScore=0        #玩家清除的方块行数
level=1     # 关卡等级
clock=None      # 游戏时钟
nowBlock=None       #当前下落中的方块
nextBlock=None      #下一个将出现的方块
fallSpeed=10        #当前方块下落速度
beginFallSpeed=fallSpeed        #游戏初始时方块下落速度
speedBuff=0     #下落速度缓冲变量
keyBuff=None        #上一次按键记录
#================== 关于blocks的变量
maxBlockWidth=10        #舞台堆叠区X轴最大可容纳基础方块数
maxBlockHeight=18       #舞台堆叠区Y轴最大可容纳基础方块数
blockWidth=30       #以像素为单位的基础方块宽度
blockHeight=30      #以像素为单位的基础方块高度
# =========================
blocks=[]       #方块形状矩阵四维列表。第一维为不同的方块形状，第二维为每个方块形状不同的方向（以0下标起始，一共四个方向），第三维为Y轴方块形状占用情况，第四维为X轴方块形状占用情况。矩阵中0表示没有方块，1表示有方块。
stage=[]        #舞台堆叠区矩阵二维列表，第一维为Y轴方块占用情况，第二维为X轴方块占用情况。矩阵中0表示没有方块，1表示有固实方块，2表示有活动方块。
gameOver=False      #游戏结束标志
pause=False     #游戏暂停标志



def getConf(fileName):
    global blocks # blocks 记录方块形状。
    with open(fileName,'rt') as fp:
        for temp in fp.readlines():
            blocks.append([])
            blocksNumb = len(blocks)-1
            blocks[blocksNumb]=[]
            #每种方块形状有四个方向，以0~3表示。
            blocks[blocksNumb].append([])  # 此时 blocks有了 x轴和 y 轴 blocks[x][y]
            row=temp.split(";")   # 用split()方法对文件进行 切片。。
            for r in range(len(row)):
                col = []
                ct = row[r].split(",")
                # 对矩阵列数据做规整，首先将非‘1’的值全修正为“0” 以过滤空字符串或者回车符
                for c in range(len(ct)):
                        if ct[c]!="1":
                            col.append(0)
                        else:
                            col.append(1)
                # 将不足4列的矩阵通过补“0”的方式，补足4列。
                for c in range(len(ct)-1,3):
                    col.append(0)
                blocks[blocksNumb][0].append(col)
                #如果矩阵某行没有方块，则配置文件中可以省略此行，程序会在末尾补上空行数据。
            for r in range(len(row)-1,3):
                blocks[blocksNumb][0].append([0,0,0,0])  
            blocks[blocksNumb][0]=formatBlock(blocks[blocksNumb][0])
            
def sysInit():
    '''
    系统初始化
    包括pygame 环境初始化，全局变量赋值，生成每个方块形状的四个方向矩阵
    '''
    global defaultFont,screen,backSurface,clock,blocks,stage,gameOver,fallSpeed,beginFallSpeed,nowBlock,nextBlock,score,level,clearLineScore,pause

    #pygame 运行环境初始化
    pg.init()
    screen = pg.display.set_mode((500,550),0,32)  # 创建窗口
    backSurface = pg.Surface((screen.get_rect().width,screen.get_rect().height))
    pg.display.set_caption("block")
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    # 游戏全局变量初始化
    defaultFont = pg.font.Font("res/font/yh.ttf",16)
    nowBlock = None
    nextBlock = None
    gameOver = False
    score = 0
    level = 1
    clearLineScore = 0
    beginFallSpeed =20
    fallSpeed = beginFallSpeed-level*2

    #初始化游戏舞台

    stage= []
    for y in range(maxBlockHeight):
        stage.append([])
        for x in range(maxBlockWidth):
            stage[y].append(EMPTY_CELL)
    #生成每个方块形状4个方向的矩阵数据

    for x in range(len(blocks)):
        # 因为重新开始游戏时会调用sysInit()对系统所有参数重新初始化，为了避免方向矩阵数据重新生成，需要在此判断是否已经生成，如果已经生成则跳过
        if len(blocks[x])<2:
            t = blocks[x][0]
            for i in range(3):
                t = transform(t,1)
                blocks[x].append(formatBlock(t))


# transform,removeTopBlank,formatBlock这三个函数只为生成方块形状4个方向矩阵使用，在游戏其他环节无作用,在阅读程序时可以先跳过。
def transform(block, direction=0):
    '''
    生成指定方块形状转换方向后的矩阵数据
    args:
        block:方块形状矩阵参数
        direction:转换的方向，0代表向左，1代表向右
    return:
        变换方向后的方块形状矩阵参数
    '''
    result = []
    for y in range(4):
        result.append([])
        for x in range(4):
            if direction == 0:
                result[y].append(block[x][3 - y])
            else:
                result[y].append(block[3 - x][y])
    return result


def removeTopBlank(block):
    '''
    清除方块矩阵顶部空行数据
    args:
        block:方块开关矩阵
    return:
        整理后的方块矩阵数据
    '''
    result = copy.deepcopy(block)
    blankNumb = 0
    while sum(result[0]) < 1 and blankNumb < 4:
        del result[0]
        result.append([0, 0, 0, 0])
        blankNumb += 1
    return result


def formatBlock(block):
    '''
    整理方块矩阵数据，使方块在矩阵中处于左上角的位置
    args:
        block:方块开关矩阵
    return:
        整理后的方块矩阵数据
    '''
    result = removeTopBlank(block)
    # 将矩阵右转，用于计算左侧X轴线空行,计算完成后再转回
    result = transform(result, 1)
    result = removeTopBlank(result)
    result = transform(result, 0)
    return result


'''
主程序
'''
def process():
    '''
    游戏控制及逻辑处理
    '''
    global gameOver, nowBlock, nextBlock, speedBuff, backSurface, keyBuff, pause     #global 是为了在别的函数中用这些变量。

    if nextBlock is None:
        nextBlock = blockSprite(random.randint(0, len(blocks) - 1), random.randint(0, 3),
                                point(maxBlockWidth + 4, maxBlockHeight))
    if nowBlock is None:
        nowBlock = nextBlock.clone()
        nowBlock.xy = point(maxBlockWidth // 2, 0)
        nextBlock = blockSprite(random.randint(0, len(blocks) - 1), random.randint(0, 3),
                                point(maxBlockWidth + 4, maxBlockHeight))
        # 每次生成新的下落方块形状时检测碰撞，如果新的方块形状一出现就发生碰撞，则显然玩家已经没有机会了。
        gameOver = checkDeany(nowBlock)
        # 游戏失败后，要将活动方块形状做固实处理
        if gameOver:
            updateStage(nowBlock, 2)

def main():
    '''
    主程序
    '''
#    getConf("elsfk.cfg")
    sysInit()
    while True:
        process()


if __name__ == "__main__":
    main()

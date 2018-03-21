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
default_font=None        #默认字体
screen=None     # 屏幕输出对象
back_surface=None        #图像输出缓冲画板

score=0     # 玩家得分记录
clear_line_score=0        #玩家清除的方块行数
level=1     # 关卡等级
clock=None      # 游戏时钟
now_block=None       #当前下落中的方块
next_block=None      #下一个将出现的方块
fall_speed=10        #当前方块下落速度
begin_fall_speed=fall_speed        #游戏初始时方块下落速度
speed_buff=0     #下落速度缓冲变量
key_buff=None        #上一次按键记录
#================== 关于blocks的变量
max_block_width=10        #舞台堆叠区X轴最大可容纳基础方块数
max_block_height=18       #舞台堆叠区Y轴最大可容纳基础方块数
block_width=30       #以像素为单位的基础方块宽度
block_height=30      #以像素为单位的基础方块高度
# =========================
blocks=[]       #方块形状矩阵四维列表。第一维为不同的方块形状，第二维为每个方块形状不同的方向（以0下标起始，一共四个方向），第三维为Y轴方块形状占用情况，第四维为X轴方块形状占用情况。矩阵中0表示没有方块，1表示有方块。
stage=[]        #舞台堆叠区矩阵二维列表，第一维为Y轴方块占用情况，第二维为X轴方块占用情况。矩阵中0表示没有方块，1表示有固实方块，2表示有活动方块。
game_over=False      #游戏结束标志
pause=False     #游戏暂停标志



def get_conf(file_name):
    '''
    从文件‘elsfk.cfg’中读取方块的内容，配置的每一行代表一个方块，方块之间用‘;’隔开，用逗号分开矩阵列，
    0表示有方块，1表示没有方块。
    然后将方块处理成为一个3维的list. list的第一个[]为方块的形状，用0,1,2,3,4,5,6代表。
    list的第二个[]代表方块旋转的方向，0代表顺时针旋转。
    list的第三个[]为每个方块的编码，为4*4的一个list。
    '''
    global blocks  #记录方块的形状。
    with open(file_name,'rt') as fp:
        for temp in fp.readlines():
            blocks.append([])  #创建blocks的第一维，用blocks_num来记录方块的形状。blocks_num根据temp的改变而改变，为0，1，2，..
            blocks_num = len(blocks)-1  #blocks_num 从1 开始
            blocks[blocks_num] = [] # 这个开始存方块的形状也就是说同一种方块有4种形状。
            blocks[blocks_num].append([])  #这个开始存方块的具体内容，为4*4的形状。
            row = temp.split(';') #用split()方法对temp 进行切片，形成一个list  len(row)=4
            print(len(row))
            for r in range(len(row)):# len(row)=4
                col = []
                ct = row[r].split(',')    #用','对row中每一个元素进行切片
                #对矩阵进行规整，没有1的地方要补齐 在这个for 循环中除了配置中有0或1的地方，其他地方只有一个0
                for c in range(len(ct)):    #len(ct)不一定是4
                    if ct[c]!='1':
                        col.append(0)
                    else:
                        col.append(1)
                #这个for循环中对 len(ct)不是4的 c  进行补齐
                for c in range(len(ct)-1,3):
                    col.append(0)
                #然后把col的值append 到 blocks[blocks_num][0]中
                blocks[blocks_num][0].append(col)
            #此时 blocks[blocks_num][0]成为一个4*4的list
            # 根据配置文件以下循环没有意义，保险起见加上。
            for r in range(len(row) - 1, 3):
                blocks[blocksNumb][0].append([0, 0, 0, 0])
            blocks[blocks_num][0] = format_block(blocks[blocks_num][0])


'''
format_block  这个函数实现的功能为把方块数据放到左上角
remove_top_blank 这个函数实现的是把方块的最上面的一行0 删除 在最下面补一行0
transform 函数实现的 把方块旋转

'''

def remove_top_blank(block):
    '''

    :param block: 清除方块矩阵顶部空行数据  block[blocks_num][0]
    :return:整理后的方块数据
    '''
    result = copy.deepcopy(block)
    blank_num = 0
    while sum(result[0])<1 and blank_num<4:
        del result [0]
        result.append([0,0,0,0])
        blank_num =blank_num+1
    return result

def transform(block,direction = 0):
    '''

    :param block:  传进来的参数为 blocks[blocks_num][0]
    :param direction: 转换的方向，0代表逆时针，1 代表 顺时针
    :return: 变换参数后的方块形状矩阵
    '''
    result = []
    for y in range(4):
        result.append([])
        for x in range(4):
            if direction ==0:
                result[y].append(block[x][3-y])
            else:
                result[y].append(block[3-y][y])
    return result


def format_block(block):
    '''

    :param block:整理方块数据，使方块在矩阵中的左上角的位置  blocks[blocks_num][0]
    :return:
    '''
    result = remove_top_blank(block)
    #  将矩阵右转，用于计算左侧X轴空行，计算后完成后在转回
    result = transform(result,1)
    result = remove_top_blank(result)
    result = transform(result,0)
    return result


def main():
    '''
    主程序
    '''
    get_conf("elsfk.cfg")
#    sysInit()
#    while True:
#        process()


if __name__ == "__main__":
    main()

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
import sys
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


def sys_init():
    '''
    这一部分是系统的初始化，包括各项变量的初始化，pygame的初始化。
    生成每个方块的四个不懂方向的矩阵。
    :return:
    '''
    global default_font,screen,back_surface,clock,blocks,stage,game_over,fall_speed,begin_fall_speed,now_block,next_block
    global score,level,clear_line_score,pause

    #pygame 初始化
    pg.init()
    screen = pg.display.set_mode((500,550))
    back_surface = pg.Surface((screen.get_rect().width,screen.get_rect().height))
    pg.display.set_caption("Tetris")  #窗口显示的字
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)


    # 游戏全局变量初始化
    default_font = pg.font.Font("res/font/yh.ttf",16)  #雅黑字体
    now_block = None
    next_block = None
    game_over = False
    pause = False
    score = 0
    level = 1
    clear_line_score = 0
    begin_fall_speed = 20
    fall_speed = begin_fall_speed - level*2


    #初始化游戏舞台
    stage = []
    for y in range(max_block_height):
        stage.append([])
        for x in range(max_block_width):
            stage[y].append(EMPTY_CELL)

    #生成每个方块形状4个方向的矩阵数据
    for x in range(len(blocks)):
        # 因为重新开始要调用sys_init()对系统所有参数重新初始化，为了避免冲突，这里要判定一下blocks[]
        if len(blocks[x])<2:
            t = blocks[x][0]
            for i in range(3):
                t = transform(t,1)
                blocks[x].append(format_block(t))






def get_conf(file_name):
    '''
    从文件‘elsfk.cfg’中读取方块的内容，配置的每一行代表一个方块，方块之间用‘;’隔开，用逗号分开矩阵列，
    0表示有方块，1表示没有方块。
    然后将方块处理成为一个3维的list. list的第一个[]为方块的形状，用0,1,2,3,4,5,6代表。
    list的第二个[]代表方块旋转的方向，0代表顺时针旋转。
    list的第三个[]为每个方块的编码，为4*4的一个list。
    '''
    global blocks  #记录方块的形状。
    with open(file_name, 'rt') as fp:
        for temp in fp.readlines():
            blocks.append([])  #创建blocks的第一维，用blocks_num来记录方块的形状。blocks_num根据temp的改变而改变，为0，1，2，..
            blocks_num = len(blocks)-1  #blocks_num 从1 开始
            blocks[blocks_num] = [] # 这个开始存方块的形状也就是说同一种方块有4种形状。
            blocks[blocks_num].append([])  #这个开始存方块的具体内容，为4*4的形状。
            row = temp.split(";") #用split()方法对temp 进行切片，形成一个list  len(row)=4
            print(len(row))
            for r in range(len(row)):# len(row)=4
                col = []
                ct = row[r].split(",")    #用','对row中每一个元素进行切片
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
                blocks[blocks_num][0].append([0, 0, 0, 0])
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
        blank_num +=1
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
                result[y].append(block[3-x][y])
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

class BlockSprite(object):
    '''
    方块精灵类
    下落的方块全靠这个类来实现。
    attributes:
    shape: 方块形状编号
    direction：方块旋转方向编号
    xy : 方块形状左上角坐标
    block:方块形状矩阵
    '''
    def __init__(self,shape,direction,xy):
        self.shape = shape
        self.direction = direction
        self.xy = xy    #这个里面的不能封装数据

    def change_direction(self,direction):
        '''
        改变方块的方向
        direction: 1为顺时针旋转，0 为逆时针旋转。
        :param direction:
        :return:
        '''
        dir_num = len(blocks[self.shape]) - 1
        if direction == 1:
            self.direction = self.direction+1
            if self.direction>dir_num:
                self.direction = 0
        else:
            self.direction = self.direction-1
            if self.direction < 0:
                self.direction = dir_num

    def clone(self):
        '''
        克隆本体
        :return:返回自身的克隆
        '''
        return BlockSprite(self.shape,self.direction,Point(self.xy.x,self.xy.y))
    def get_blocks(self):
        return blocks[self.shape][self.direction]        #返回一个blocks[][]

    block = property(get_blocks)   # 这个装饰器在check_deany 中用到


class Point(object):
    '''
    平面坐标点类
    attributes:
    x,y :坐标值
    '''
    def __init__(self,x,y):
        self.__x = x
        self.__y = y
    @property
    def x(self):
        return self.__x
    @x.setter
    def x(self, x):
        self.__x = x

    #def get_x(self):
        #return self.__x


#    x = property(get_x,set_x)   #装饰器
    @property
    def y(self):
        return self.__y
    @y.setter
    def y(self,y):
        self.__y = y


    #def get_y(self):
        #return self.__y

    #def set_y(self,y):
        #self.__y = y

    #y = property(get_y,set_y)

    def __str__(self):
        return "{x:"+"{:.0f}".format(self.__x)+",y:"+"{:.0f}".format(self.__y)+"}"

def check_deany(sprite):
    '''
    检查下落方块是否与舞台堆叠区中间的实方块发生碰撞

    :param sprite:下落的方块。
    :return:如果碰撞 返回 True
    '''
    top_x = sprite.xy.x
    top_y = sprite.xy.y
    for y in range(len(sprite.block)):   ## sprite.blocks 为 blocks[shape][direction]
        for x in range(len(sprite.block[y])): # 这段代码是对某一个方块进行遍历，如果==1 的话
            if sprite.block[y][x] == 1:
                y_in_stage = top_y + y
                x_in_stage = top_x + x
                if y_in_stage > max_block_height - 1  or  y_in_stage<0:
                    return True
                if x_in_stage >max_block_width-1 or x_in_stage <0:
                    return True
                if stage[y_in_stage][x_in_stage] == STATIC_BLOCK:
                    return True
    return False

def update_stage(sprite,update_type = 1):
    '''
    将下落方块数据坐标更新到堆叠区中。下落的方块涉及的坐标在堆叠去中用数字1 标识，固实的方块在堆叠去中用数字2 表示。
    :param sprite: 下落方块形状
    :param update_type: 更新方式，0 代表清除，1 代表动态加入，2代表固实加入。
    :return:
    '''
    global stage
    top_x = sprite.xy.x
    top_y = sprite.xy.y
    for y in range(len(sprite.block)):
        for x in range(len(sprite.block[y])):
            if sprite.block[y][x]==1:
                if update_type == 0 :
                    if stage[top_y+y][top_x+x] ==FALLING_BLOCK:
                        stage[top_y+y][top_x+x] = EMPTY_CELL
                elif update_type == 1:
                    if stage[top_y+y][top_x+x] ==EMPTY_CELL:
                        stage[top_y+y][top_x+x] = FALLING_BLOCK
                else:
                    stage[top_y+y][top_x+x] = STATIC_BLOCK

def check_line():
    '''
    检测堆叠去是否有可消除的整行固实方块
    根据检测结果重新生成堆叠去矩阵数据，调用update_score 函数更新还价积分等数据
    :return:
    本轮下落周期消除的固实方块行数
    '''
    global stage
    clear_count = 0  # 本轮下落周期消除的固实方块行数
    tmp_stage = [] #根据消除情况新生成的堆叠区矩阵，在有更新的情况下会替换全局的堆叠去矩阵

    for y in stage:
        # 因为固实方块在堆叠区矩阵里以2 表示，所以判断防方块是否被消除只需要计算矩阵行数值合计是否等于堆叠去X轴最大方块数*2就可以。
        if sum(y)>= max_block_width*2:
            tmp_stage.insert(0,max_block_width*[0])
            clear_count = clear_count+1
        else:
            tmp_stage.append(y)

    if clear_count>0:
        stage = tmp_stage
        update_score(clear_count)
    return clear_count

def update_score(clear_count):
    '''
    更新玩家的游戏记录，包括积分，管卡，消除方块行数，并且根据关卡数更新方块下落速度。

    :param clear_count:本轮下落周期内消除的方块行数。
    :return:当前游戏的最新积分
    '''

    global score,fall_speed,level,clear_line_score

    prize_point=0  # 额外奖励分数，同时消除的行数越多，奖励分值越高
    if clear_count>1:
        if clear_count<4:
            prize_point = clear_count**clear_count

        else:
            prize_point = clear_count*5
    score = score+(clear_count+prize_point)*level

    if score>99999999:
        score = 0

    clear_line_score = clear_line_score+clear_count

    if clear_line_score>100:
        clear_line_score = 0
        level = level+1

        if level>(begin_fall_speed/2):
            level = 1
            fall_speed = begin_fall_speed
        fall_speed = begin_fall_speed-level*2
    return  score

def printTxt(content,x,y,font,screen,color=(255,255,255)):


    imgTxt = font.render(content,True,color)
    screen.blit(imgTxt,(x,y))


def draw_stage(draw_screen):
    '''
    在给定的画布上绘制舞台
    :param draw_screnn: 待绘制的画布
    :return:
    '''
    static_color = 30,102,76  # 固实方块颜色
    active_color = 255,239,0 #方块形状颜色
    font_color =200,10,120 # 文字颜色

    base_rect = 0,0,block_width*max_block_width+1,block_height*max_block_height+1   #堆叠去方框
    #绘制堆叠去外框
    draw_screen.fill((180,200,170))
    pg.draw.rect(draw_screen,static_color,base_rect,1)

    #绘制堆叠去内所有的方块，包括下落方块形状
    for y in range(len(stage)):
        for x in range(len(stage[y])):
            base_rect = x*block_width,y*block_height,block_width,block_height
            if stage[y][x]==2:
                pg.draw.rect(draw_screen,static_color,base_rect)
            elif stage[y][x] == 1:
                pg.draw.rect(draw_screen,active_color,base_rect)

        # 绘制下一个登场的下落方块形状
        printTxt("下一个：",320,350,default_font,back_surface,font_color)
        if next_block != None:
            for y in range(len(next_block.block)):
                for x in range(len(next_block.block[y])):
                    base_rect = 320+x*block_width,380+y*block_height,block_width,block_height
                    if next_block.block[y][x] == 1:
                        pg.draw.rect(draw_screen,active_color,base_rect)


        #绘制当前关卡、积分、当前关卡消除整行数
        printTxt("等级：%d" % level,320,40,default_font,back_surface,font_color)
        printTxt("分数：%d" % score,320,70,default_font,back_surface,font_color)
        printTxt("已消除:%d行" % clear_line_score,320,100,default_font,back_surface,font_color)


        #特殊游戏状态的输入

        if game_over:
            printTxt("完蛋啦",230,200,default_font,back_surface,font_color)
            printTxt("<按'RETURN'重新开始>",200,260,default_font,back_surface,font_color)

        if pause:
            printTxt("干嘛去啦，怎么不来玩我",230,200,default_font,back_surface,font_color)
            printTxt("快点继续啦，请按'RETURN'",200,260,default_font,back_surface,font_color)


def process():
    '''
    游戏逻辑控制
    '''
    global game_over,now_block,next_block,speed_buff,back_surface,key_buff,pause
    if next_block is None:
        next_block = BlockSprite(random.randint(0,len(blocks)-1),random.randint(0,3),Point(max_block_width+4,max_block_height))
    if now_block is None:
        now_block = next_block.clone()  # 克隆block
        now_block.xy = Point(max_block_width//2,0)   # 把next_block中的坐标改为 在舞台中间
        next_block = BlockSprite(random.randint(0,len(blocks)-1),random.randint(0,3),Point(max_block_width+4,max_block_height))
        # 方块下落时要检测是否 gameover
        game_over = check_deany(now_block)
        if game_over:
            update_stage(now_block,2)
    '''
    对下落的方块方块形状操控以及移动，采用影子形状进行预判断。如果没有碰撞则将变化应用到正在下落的方块上，否则不变化。
    '''

    tmp_block = now_block.clone()

    '''
    处理用户输入
    对于用户输入分为两部分处理。
    1、将退出、暂停、重新开始以及形状的变换的操作当做敲击事件处理。这样的好处是对只敲一次键盘作出处理，
    避免用户按住单一按键后程序反复处理影响操控，特别是变换形状操作，敲击一次键盘变换一次形状，玩家很容易操作。
    '''
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
            pg.quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                sys.exit()
                pg.quit()
            elif event.key == pg.K_RETURN:
                if game_over:
                    sys_init()
                    return
                elif pause:
                    pause = False
                else:
                    pause = True
                    return
            elif not game_over and not pause:
                if event.key == pg.K_SPACE:
                    tmp_block.change_direction(1)
                elif event.key == pg.K_UP:
                    tmp_block.change_direction(0)
    if not game_over and not pause:
        '''
        2、将左右移动和快速下落的操作按以下事件处理。
        这样做的好处是不需要玩家反复敲击键盘进行操作，保证了程序的连贯性。
        由于连续移动的速度太快，不利于定位。所以在程序中采用了简单的输入减缓处理，即通过keyBuff 保存上一次的按键，如果此次按键和
        上次的相同，则跳过此轮按键处理。
        '''
        keys = pg.key.get_pressed()
        if keys[K_DOWN]:
            tmp_block.xy = Point(tmp_block.xy.x,tmp_block.xy.y+1)
            key_buff = None
        elif keys[K_LEFT]:
            if key_buff!=pg.K_LEFT:
                tmp_block.xy = Point(tmp_block.xy.x-1,tmp_block.xy.y)
                key_buff = pg.K_LEFT
            else:
                key_buff = None
        elif keys[K_RIGHT]:
            if key_buff!=pg.K_RIGHT:
                tmp_block.xy = Point(tmp_block.xy.x+1,tmp_block.xy.y)
                key_buff = pg.K_RIGHT
            else:
                key_buff = None
        if not check_deany(tmp_block):
            update_stage(now_block,0)
            now_block = tmp_block.clone()


        #处理自动下落
        speed_buff = speed_buff+1
        if speed_buff>=fall_speed:
            speed_buff = 0
            tmp_block = now_block.clone()
            tmp_block.xy = Point(now_block.xy.x,now_block.xy.y+1)
            if not check_deany(tmp_block):
                update_stage(now_block,0)
                now_block = tmp_block.clone()
                update_stage(now_block,1)
            else:
                #在自动下落的过程中一旦发生活动方块的碰撞，则将活动方块做固实处理，并检测是否有可消除的整行方块
                update_stage(now_block,2)
                check_line()
                now_block = None
        else:
            update_stage(now_block,1)
    draw_stage(back_surface)
    screen.blit(back_surface,(0,0))
    pg.display.update()
    clock.tick(30)

def main():
    '''
    主程序
    '''
    get_conf("elsfk.cfg")
    sys_init()
    while True:
       process()


if __name__ == "__main__":
    main()

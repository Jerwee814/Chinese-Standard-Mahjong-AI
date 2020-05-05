import json
from MahjongGB import MahjongFanCalculator
import numpy as np
import random
import function
'''
#version 0.1: random
def DisCard(data,extra_card=None):
    #return discard and data
    play_ID, quan, pack, hand, hua = data["info"]
    card = data["card"]
    if extra_card!=None:
        hand.append(str_to_num(extra_card))
    dis_card = hand[random.randint(0,len(hand))-1]
    hand.remove(dis_card)
    dis_card = num_to_str(dis_card)
    data = {
          "info":[play_ID, quan, pack, hand, hua],
          "card":card,
          "pre_require":"",
          "pre_card":dis_card
    }
    if extra_card!=None:
        data["pre_require"]="DRAW"
    return dis_card, data


#version 0.2:first play 中发白, Wind then single card

def DisCard(data,extra_card=None):
    play_ID, quan, pack, hand, hua = data["info"]
    card = data["card"]
    if extra_card!=None:
        hand.append(str_to_num(extra_card))
    hand.sort()
    discard = hand[0]
    if hand[-1]>=30:
        discard = hand[-1]
        hand.pop()
    else:
        pair = False
        for i in range(len(hand)):
            if (i+1<len(hand) and hand[i]==hand[i+1]) or (i>0 and hand[i]==hand[i-1]):
                continue
            discard = hand[i]
            del hand[i]
            pair=True
            break
        if pair==False:
            discard = hand[random.randint(0,len(hand))-1]
            hand.remove(discard)

    discard = num_to_str(discard)
    data = {
          "info":[play_ID, quan, pack, hand, hua],
          "card":card,
          "pre_require":"",
          "pre_card":discard
    }
    if extra_card!=None:
        data["pre_require"]="DRAW"
    return discard, data

##version 0.3:
#若中发白风有对子，则保留，否则优先中发白风
#有对子保留，有顺子也尽量保留，然后再走单牌
def DisCard(data,extra_card=None):##extra_card表示抽到的牌;  ps:peng,chi也需要打一张牌，此时没有extra_card
    play_ID, quan, pack, hand, hua = data["info"]
    card = data["card"]
    if extra_card!=None:
        hand.append(str_to_num(extra_card))
    hand.sort()
    discard = hand[0]
    ##判断是否有中发白风
    find_card = True
    if hand[-1]>=30:
        i=-1
        discard = hand[i]
        while((i>-len(hand) and discard==hand[i-1]) or discard==hand[i+1]):
            i-=1
            if i<-len(hand):
                find_card=False
                break
            discard=hand[i]
        if find_card:
            hand.remove(discard)
    else:
        find_card=False
    ##没有中发白风
    if find_card==False:
        find_card = True
        for i in range(len(hand)):
            if (i+1<len(hand) and hand[i]==hand[i+1]) or (i>0 and hand[i]==hand[i-1]):
                #是对子
                continue
            if (i+1<len(hand) and hand[i]==hand[i+1]-1 and hand[i]==hand[i-1]+1)\
                or (hand[i]==hand[i-1]+1 and hand[i]==hand[i-2]+2)\
                or (i+2<len(hand) and hand[i]==hand[i+1]-1 and hand[i]==hand[i+2]-2):
                #是顺子
                continue
            discard = hand[i]
            del hand[i]
            find_card=True
            break
        ##全都是对子或顺子，则随机打一张
        if find_card==False:
            discard = hand[random.randint(0,len(hand))-1]
            hand.remove(discard)

    discard = num_to_str(discard)
    data = {
          "info":[play_ID, quan, pack, hand, hua],
          "card":card,
          "pre_require":"",
          "pre_card":discard
    }
    if extra_card!=None:
        data["pre_require"]="DRAW"
    return discard, data
'''
#old version above

##version 0.4:
#若中发白风有对子，则保留，否则优先中发白风
#有对子保留，有顺子也尽量保留，然后再走单牌
#走单牌时，按照单牌离相同种类的牌的最小距离排序，输出距离最大的牌
#example:W1 W3 W7,优先出W7； W1 W3 W7 B1,优先出B1
def DisCard(data,extra_card=None):##extra_card表示抽到的牌;  ps:peng,chi也需要打一张牌，此时没有extra_card
    play_ID, quan, pack, hand, hua = data["info"]
    card = data["card"]
    if extra_card!=None:
        hand.append(str_to_num(extra_card))
    hand.sort()
    discard = hand[0]
    ##判断是否有中发白风
    find_card = True
    if hand[-1]>=30:
        i=-1
        discard = hand[i]
        while((i>-len(hand) and discard==hand[i-1]) or discard==hand[i+1]):
            i-=1
            if i<-len(hand):
                find_card=False
                break
            discard=hand[i]
        if find_card:
            hand.remove(discard)
    else:
        find_card=False
    ##没有中发白风
    single_card = []##保存可能的单牌的index
    if find_card==False:
        for i in range(len(hand)):
            if (i+1<len(hand) and hand[i]==hand[i+1]) or (i>0 and hand[i]==hand[i-1]):
                #是对子
                continue
            if (i+1<len(hand) and hand[i]==hand[i+1]-1 and hand[i]==hand[i-1]+1)\
                or (hand[i]==hand[i-1]+1 and hand[i]==hand[i-2]+2)\
                or (i+2<len(hand) and hand[i]==hand[i+1]-1 and hand[i]==hand[i+2]-2):
                #是顺子
                continue
            single_card.append(i)
            #discard = hand[i]
            #del hand[i]
            find_card=True

        if find_card==True:
            distance = []
            for index in single_card:
                item = hand[index]
                pre = hand[index-1]
                last = None
                dis = 100##初始化最大的distance
                if index+1<len(hand):
                    last = hand[index+1]
                if (item//10==pre//10):##属于同一种类
                    dis = item-pre
                if last!=None and (item//10==last//10):
                    dis = min(dis, last-item)
                distance.append(dis)
            index = distance.index(max(distance))##找到最大距离的索引
            discard = hand[single_card[index]]
            hand.remove(discard)
        ##全都是对子或顺子，则随机打一张
        else:
            discard = hand[random.randint(0,len(hand))-1]
            hand.remove(discard)

    discard = num_to_str(discard)
    data = {
          "info":[play_ID, quan, pack, hand, hua],
          "card":card,
          "pre_require":"",
          "pre_card":discard
    }
    if extra_card!=None:
        data["pre_require"]="DRAW"
    return discard, data
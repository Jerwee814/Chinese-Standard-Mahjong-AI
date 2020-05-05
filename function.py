import json
from MahjongGB import MahjongFanCalculator
import numpy as np
import random

def str_to_num(card):
    #将麻将的字符转换成数字表示
    #W1-W9 -> 1-9
    #B1-B9 -> 11-19
    #T1-T9 -> 21-29
    #F1-F4 J1-J3 ->31-37
    #H1-H8 -> 0
    if card[0]=="W":
        return int(card[1])
    if card[0]=="B":
        return 10+int(card[1])
    if card[0]=="T":
        return 20+int(card[1])
    if card[0]=="H":
        return 0
    if card[0]=="F" :
        return 30+int(card[1])
    if card[0]=="J":
        return 34+int(card[1])

def num_to_str(card):
    #将麻将的数字表示转换成字符表示
    x = card%10
    s = card//10
    if s == 0:
        return "W"+str(x)
    if s==1:
        return "B"+str(x)
    if s==2:
        return "T"+str(x)
    if s==3:
        if x>4:
            return "J"+str(x-4)
        else:
            return "F"+str(x)


def code_card(hand):
    #hand = list["W0","B1",...,"B2"] -> lsit[int,int,int]
    #将手牌中的麻将字符表示转换成数字表示，并返回list
    new_hand = []
    for card in hand:
        new_hand.append(str_to_num(card))
    return new_hand

def decode_card(hand):
    #将手牌中的麻将数字表示转换成字符表示，并返回tuple
    #return tuple
    new_hand = []
    for card in hand:
        new_hand.append(num_to_str(card))
    return tuple(new_hand)
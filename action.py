import json
from MahjongGB import MahjongFanCalculator
import numpy as np
import random
import function
from discard import DisCard


def Can_Hu(extra_card, data, is_ZIMO):
    ## give extra_card(draw or others play), judge if can HU and return 
    # if_Hu(bool), action, data
    play_ID, quan, pack, hand, hua = data["info"]
    #将list转换成tuple
    new_pack = []
    for item in pack:
        new_pack.append(tuple(item))
    new_pack = tuple(new_pack)
    try:
        new_hand = decode_card(hand)#transfer list[int] -> list[string]
        ans=MahjongFanCalculator(new_pack,new_hand,extra_card,hua,is_ZIMO,False,False,False,play_ID,quan)
        fan = 0
        for item in ans:
            fan+=item[0]
        fan = fan-hua
        if fan<8:#未到8番
            raise Exception
    except Exception as err:
            #not HU
        return False, "", ""
    else:
        action = "HU"
        data = ""
        return True, action, data

    

def Can_Gang(ID,extra_card, data):
    ## give extra_card(draw or others play), judge if can GANG and return 
    # if_Gang(bool), action, data
    play_ID, _, _, hand, _ = data["info"]
    extra_card = str_to_num(extra_card)
    count = 0
    for card in hand:
        if card==extra_card:
            count+=1
    if count==3:##there are 3 same cards in hand and they are equal to extra_card, so we can gang
        GANG = ["GANG",num_to_str(extra_card),(play_ID-ID+4)%4]
        data["info"][2].append(GANG)##add gang to pack
        ##delete gang card in hand
        while(extra_card in hand):
            hand.remove(extra_card)
        data["info"][3]=hand
        return True, "GANG", data
    else:
        return False, None, None

def Can_BuGang(ID,extra_card, data):
    ## give extra_card(draw or others play), judge if can BUGANG and return 
    # if_BuGang(bool), action, data
    pack = data["info"][2]
    for i, item in enumerate(pack):
        if item[0]=="PENG" and extra_card==item[1]:#find a peng and its peng card is equal to extra_card,so bugang
            data["info"][2][i][0]="GANG"
            return True, "BUGANG "+extra_card, data
    return False,None,None


def Can_Peng(ID,extra_card, data):
    ## give extra_card(draw or others play), judge if can PENG and return 
    # if_Peng(bool), action, data
    play_ID, _, _, hand, _ = data["info"]
    extra_card = str_to_num(extra_card)
    count = 0
    for card in hand:
        if card==extra_card:
            count+=1
    if count==2:##there are 2 same cards in hand and they are equal to extra_card, so we can gang
        PENG = ["PENG",num_to_str(extra_card),(play_ID-ID+4)%4]
        data["info"][2].append(PENG)##add gang to pack
        while(extra_card in hand):
            hand.remove(extra_card)
        data["info"][3]=hand
        discard, data = DisCard(data)
        return True, "PENG "+discard, data
    else:
        return False, None, None


def Can_Chi(extra_card, data):
    ## give extra_card(draw or others play), judge if can CHI and return 
    # if_Chi(bool), action, data
    extra_card = str_to_num(extra_card)
    _, _, _, hand, _ = data["info"]
    hand.sort()
    if extra_card>=30:
        return False, None, None##风、中发白不能chi
    CHI = None
    ##判断是否能chi，顺序确定(可修改)
    if extra_card-1 in hand:
        if extra_card-2 in hand:
            CHI = ["CHI", num_to_str(extra_card-1), 3]
            data["info"][2].append(CHI)
            data["info"][3].remove(extra_card-1)
            data["info"][3].remove(extra_card-2)
            discard, data = DisCard(data)
            return True, "CHI "+num_to_str(extra_card-1)+" "+discard, data
        elif extra_card+1 in hand:
            CHI = ["CHI", num_to_str(extra_card), 2]
            data["info"][2].append(CHI)
            data["info"][3].remove(extra_card-1)
            data["info"][3].remove(extra_card+1)
            discard, data = DisCard(data)
            return True, "CHI "+num_to_str(extra_card)+" "+discard, data
    else:
        if extra_card+1 in hand and extra_card+2 in hand:
            CHI = ["CHI", num_to_str(extra_card+1), 2]
            data["info"][2].append(CHI)
            data["info"][3].remove(extra_card+2)
            data["info"][3].remove(extra_card+1)
            discard, data = DisCard(data)
            return True, "CHI "+num_to_str(extra_card+1)+" "+discard, data

    return False, None, None


def Action(curr_input, input_data):##for the newest request,my action
    card = input_data["card"]
    play_ID = input_data["info"][0]
    curr_input = curr_input.split(" ")
    requests_ID = int(curr_input[0])
    if requests_ID==2:#if I draw a card
        other_ID = play_ID
        get_card = curr_input[1]
        card[str_to_num(get_card)]+=1#已知牌池增加
        if_HU, action, data = Can_Hu(get_card, input_data, is_ZIMO=True)#whether i can hu?
        if if_HU:
            return action, data

        if_Gang, action, data = Can_Gang(other_ID,get_card, input_data)#whether i can 暗gang
        if if_Gang:
            return action+" "+get_card, data
        
        if_BuGang, action, data = Can_BuGang(other_ID,get_card, input_data)#whether i can bugang
        if if_BuGang:
            return action, data
            
        discard, data = DisCard(input_data,get_card)#discard
        action = "PLAY "+discard
        return action, data
    other_ID = int(curr_input[1])
    #other requests
    if requests_ID==3 and other_ID!=play_ID:
        other_action = curr_input[2]
        if other_action=="BUHUA" or other_action=="DRAW":#other buhua or draw
            action = "PASS"
            data = input_data
            return action, data

        if (other_action=="PLAY" and other_ID!=play_ID) or other_action=="PENG" or other_action=="CHI":
            if other_action=="CHI":#other chi
                played_card = curr_input[4]
                CHI_card = curr_input[3]
                CHI_card = str_to_num(CHI_card)
                ##更新已知牌池
                card[CHI_card-1]+=1
                card[CHI_card]+=1
                card[CHI_card+1]+=1
            else:
                played_card = curr_input[3]
                if other_action=="PENG":#other peng
                    PENG_card = input_data["pre_card"]
                    card[str_to_num(PENG_card)]+=3
            #other play a card(包括chi,peng后打的牌)
            input_data["pre_card"] = played_card
            if_HU, action, data = Can_Hu(played_card, input_data, is_ZIMO=False)
            if if_HU:
                return action, data

            if_Peng, action, data = Can_Peng(other_ID,played_card, input_data)
            if if_Peng:
                return action, data

            if_Gang, action, data = Can_Gang(other_ID,played_card, input_data)
            if if_Gang:
                return action, data
            if play_ID==(other_ID+1)%4:
                if_Chi, action, data = Can_Chi(played_card, input_data)
                if if_Chi:
                    return action, data

        if other_action=="GANG":#other gang
            if input_data["pre_require"]!="DRAW":
                GANG_card = input_data["pre_card"]
                card[str_to_num(GANG_card)]=4

        if other_action=="BUGANG":#other bugang
            BUGANG_card = curr_input[3]
            card[str_to_num(BUGANG_card)]=4
        input_data["pre_require"] = other_action
        action="PASS"
        data = input_data
        return action, data
    return "PASS", input_data
import json
from MahjongGB import MahjongFanCalculator
import numpy as np
import random
import function
from action import Action

'''
一些描述：
    data："info"=[play_ID, quan, pack(吃杠碰),hand(手牌), 补花数]
            //pack,hand为list, 其余为int; 
            pack中麻将为字符表示，hand中麻将为数字表示
          "card"存放已知牌池
          "pre_card"上一张打出的牌；若无则为""
          "pre_require"上一个指令(判断别人是否暗杆)；若无则为""
'''


def recover_data(requests, responses):
    #recover data and return data
    #len(requests)=turn
    #len(responses)=turn-1
    if len(requests)==1:#the first turn, no data to recover
        return None

    if len(requests)==2:#the second turn, recover play_ID,quan
        request = requests[0].split(' ')
        play_ID = int(request[1])
        quan = int(request[2])
        data = {
            "info":[play_ID,quan,None,None,None]
        }
        return data
    Turn_ID = len(requests)
    card = [0 for _ in range(38)]##牌池
    pre_card=""
    pre_require=""
    hand = []#手牌
    pack = []#peng，gang，chi牌
    hua = 0
    play_ID = 0
    quan = 0
    turn = 0
    for request, response in zip(requests,responses):#for all input and my answer
        turn+=1
        request = request.split(' ')
        response = response.split(' ')
        if int(request[0])==0:#the first turn
            play_ID = int(request[1])
            quan = int(request[2])
        if int(request[0]) == 1:#the second turn,recover hand
            hua = int(request[play_ID+1])
            hand = request[5:18]
            hand = code_card(hand)
            for item in hand:
                card[item]+=1
        if int(request[0])==2:#draw a card
            draw_card = request[-1]
            hand.append(str_to_num(request[-1]))
            card[hand[-1]]+=1
            if response[0]=="PLAY":#what do I play?
                hand.remove(str_to_num(response[-1]))
                pre_card=response[-1]
            if response[0]=="GANG":#or if I 暗gang?
                pack.append(["GANG",draw_card, 0])
                for i in range(4):
                    hand.remove(str_to_num(draw_card))
            if response[0]=="BUGANG":#or if I bugang
                for i in range(len(pack)):
                    if pack[i][1]==draw_card:
                        pack[i][0]="GANG"
                        hand.remove(str_to_num(draw_card))
                        break

        if int(request[0])==3:#other operator
            if int(request[1])==play_ID:#my own operator(play card,暗gang,bugang), i had aready recovered
                if request[2]=="BUHUA":
                    hua+=1
                continue

            if request[2]=="PLAY" or request[2]=="PENG" or request[2]=="CHI":
                pre_card = request[-1]
                if request[2]=="PLAY":#other play
                    card[str_to_num(request[-1])]+=1
                    pre_card=request[-1]
                if request[2]=="PENG":#other peng
                    card[str_to_num(request[-1])]+=3
                if request[2]=="CHI":#other chi
                    card[str_to_num(request[-1])]+=1
                    card[str_to_num(request[-2])]+=1
                    card[str_to_num(request[-2])+1]+=1
                    card[str_to_num(request[-2])-1]+=1
                if response[0]=="PENG":#other play a card and I peng
                    pack.append(["PENG",pre_card,(int(request[1])-play_ID+4)%4])
                    hand.remove(str_to_num(pre_card))
                    hand.remove(str_to_num(pre_card))
                    hand.remove(str_to_num(response[-1]))
                    pre_card=response[-1]
                if response[0]=="CHI":#other play a card and I chi
                    ##没有被人抢碰或抢杠
                    last_request = requests[turn].split(' ')
                    if (last_request[2]!="PENG" and last_request[2]!="GANG"):
                        which_card = 2+str_to_num(pre_card)-str_to_num(response[1])
                        pack.append(["CHI", response[1],which_card])
                        for i in range(3):
                            if i+1!=which_card:
                                hand.remove(str_to_num(response[1])-1+i)
                        pre_card = response[-1]
                        hand.remove(str_to_num(response[-1]))

                if response[0]=="GANG":#other play a card and I gang
                    pack.append(["GANG",pre_card,(int(request[1])-play_ID+4)%4])
                    for i in range(3):
                        hand.remove(str_to_num(pre_card))
            if request[2]=="BUGANG":#other bugang
                card[str_to_num(request[-1])]=4
            if request[2]=="GANG":#other gang
                if pre_require!="DRAW":#other not 暗gang
                    card[str_to_num(pre_card)]=4

            if request[2]=="DRAW":#other draws
                pre_require="DRAW"
            else:
                pre_require=""

    hand.sort()
    '''若初始手牌中有4个相同的，直接暗杠
    An_GANG=[]
    for i in range(len(hand)):
        if i<len(hand)-3:
            if hand[i]==hand[i+1] and hand[i+1]==hand[i+2] and hand[i+2]==hand[i+3]:
                An_GANG.append(hand[i])
                pack.append(["GANG",num_to_str(hand[i]),0])
    for item in An_GANG:
        while(item in hand):
            hand.remove(item)
    '''

    data = {
            "info":[play_ID,quan,pack,hand,hua],
            "card":card,
            "pre_require":pre_require,
            "pre_card":pre_card
        }
    return data



def main():
    ##loading(debug mode)
    '''
    test_input = json.dumps(
{"requests":["0 1 1","1 1 1 1 1 F4 J3 W7 B7 T3 T1 B9 B5 B2 F4 W2 T1 W1 H1 H5 H7 H4","3 0 DRAW","3 0 PLAY B9","2 B4","3 1 PLAY J3","3 2 DRAW","3 2 PLAY B6","3 3 DRAW","3 3 PLAY J2","3 0 DRAW","3 0 PLAY F1","2 W7","3 1 PLAY T3","3 2 DRAW","3 2 PLAY B5","3 3 CHI B5 B2","3 0 DRAW","3 0 PLAY F2","2 W6","3 1 PLAY B2","3 2 DRAW","3 2 PLAY B6","3 3 DRAW","3 3 PLAY F1","3 0 DRAW","3 0 PLAY B3","3 1 CHI B4 B7","3 2 BUHUA H8","3 2 DRAW","3 2 PLAY B8","3 3 DRAW","3 3 PLAY J3","3 0 DRAW","3 0 PLAY J1","3 2 PENG F1","3 3 DRAW","3 3 PLAY B9","3 0 DRAW","3 0 PLAY T9","2 W3","3 1 PLAY B9","3 2 DRAW","3 2 PLAY F2","3 3 DRAW","3 3 PLAY W1","3 0 DRAW","3 0 PLAY F3","2 J2","3 1 PLAY J2","3 2 DRAW","3 2 PLAY F3","3 3 DRAW","3 3 PLAY B3","3 0 DRAW","3 0 PLAY T5","3 3 PENG T6","3 0 DRAW","3 0 PLAY T2","2 F2","3 1 PLAY F2","3 2 DRAW","3 2 PLAY B1","3 0 PENG T6","2 F3","3 1 PLAY F3","3 2 DRAW","3 2 PLAY B5","3 3 DRAW","3 3 PLAY B2","3 0 DRAW","3 0 PLAY F1","3 1 BUHUA H2","2 T8","3 1 PLAY T8","3 2 CHI T7 T1","3 1 PENG W6","3 2 CHI W7 W6","3 3 DRAW","3 3 PLAY J3","3 0 DRAW","3 0 PLAY W6","2 T8","3 1 PLAY T8","3 2 DRAW","3 2 PLAY F2","3 3 DRAW","3 3 PLAY W9","3 0 BUHUA H6","3 0 DRAW","3 0 PLAY W5","2 B9","3 1 PLAY B9","3 2 DRAW","3 2 PLAY B4","3 3 DRAW","3 3 PLAY T6","3 0 CHI T7 W1","3 1 CHI W2 W1","3 2 DRAW","3 2 PLAY W3","3 3 DRAW","3 3 PLAY T9","3 0 DRAW","3 0 PLAY W4","2 F4","3 1 PLAY W7","3 2 DRAW","3 2 PLAY W9","3 3 DRAW","3 3 PLAY B6","3 0 DRAW","3 0 PLAY W9","2 J1","3 1 PLAY J1","3 2 DRAW","3 2 PLAY B8","3 3 DRAW","3 3 PLAY T7","3 0 DRAW","3 0 PLAY T9","2 B3","3 1 PLAY B3","3 2 BUHUA H3","3 2 DRAW","3 2 PLAY B1","3 3 DRAW","3 3 PLAY B7","3 0 DRAW","3 0 PLAY J3","2 F4","3 1 GANG","2 W5","3 1 PLAY W7","3 2 DRAW","3 2 PLAY T8","3 3 DRAW","3 3 PLAY B8","3 0 DRAW","3 0 PLAY T4","2 B7","3 1 PLAY W5","3 2 DRAW","3 2 PLAY W9","3 3 DRAW","3 3 PLAY W4","3 0 DRAW","3 0 PLAY T4","2 T2","3 1 PLAY B7","3 2 DRAW","3 2 PLAY W7","3 3 DRAW","3 3 PLAY B7","3 0 DRAW","3 0 PLAY B4","2 B5","3 1 PLAY B5","3 2 DRAW","3 2 PLAY T7","3 3 DRAW","3 3 PLAY J2","3 0 DRAW","3 0 PLAY T4","2 B3","3 1 PLAY B3","3 2 DRAW","3 2 PLAY T9","3 3 DRAW","3 3 PLAY F3","3 0 DRAW","3 0 PLAY T3","2 J2","3 1 PLAY J2","3 2 DRAW","3 2 PLAY B8","3 3 DRAW","3 3 PLAY T2"],"responses":["PASS","PASS","PASS","PASS","PLAY J3","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY T3","PASS","PASS","PASS","PASS","PASS","PASS","PLAY B2","PASS","PASS","PASS","PASS","PASS","PASS","CHI B4 B7","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY B9","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY J2","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY F2","PASS","PASS","PASS","PASS","PLAY F3","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY T8","PASS","PENG W6","PASS","PASS","PASS","PASS","PASS","PASS","PLAY T8","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY B9","PASS","PASS","PASS","PASS","PASS","CHI W2 W1","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY W7","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY J1","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY B3","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PASS","GANG F4","PASS","PLAY W7","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY W5","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY B7","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY B5","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY B3","PASS","PASS","PASS","PASS","PASS","PASS","PASS","PLAY J2","PASS","PASS","PASS","PASS"]}
    )
    full_input = json.loads(test_input)
    '''
    ##loading(bot mode)
    full_input = json.loads(input())

    # 分析自己收到的输入和自己过往的输出，并恢复状态
    all_requests = full_input["requests"]
    all_responses = full_input["responses"]
    my_data = recover_data(all_requests, all_responses)

    # 看看自己最新一回合输入
    curr_input = all_requests[-1]

    # TODO: 作出决策并输出
    if my_data!=None:
        play_ID, quan, pack, hand, hua = my_data["info"]

    if len(all_requests) == 1:#the first turn
        requests = all_requests[0].split(' ')
        play_ID = int(requests[1])
        quan = int(requests[2])
        my_data = {
                "info":[play_ID,quan,None,None,None]
        }
        my_action = "PASS"
    elif len(all_requests) == 2:# the second turn
        requests = all_requests[1].split(' ')
        hua = int(requests[play_ID+1])
        hand = requests[5:18]
        hand = code_card(hand)
        card = [0 for _ in range(38)]
        for i in hand:
            card[i] += 1
        my_data = {
                "info":[play_ID, quan, (), hand, hua],
                "card":card
        }
        my_action = "PASS"
    else:#other turns
        my_action, my_data = Action(curr_input, my_data)

    #output
    print(json.dumps({
        "response": my_action,
        "debug":my_data
    }))

if __name__ == '__main__':
    main()
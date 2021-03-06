#!/bin/env python
# -*- coding: utf-8 -*-
''' grab lol player info from 178 API '''
import urllib
import urllib2
import bs4
import sys
import re
import json
import datetime

def post(url, data):
    ''' copy from web post method '''
    req = urllib2.Request(url)
    if data != None:
        data = urllib.urlencode(data)
    #enable cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    try:
        response = opener.open(req, data, timeout=5)
        ret = response.read()
    except:
        print 'read timeout'
        return ''
    return ret

def get(url, data):
    ''' url get method '''
    data = urllib.urlencode(data)
    url += "?" + data
    return post(url, None)

def getPlayerMatch(p_server, p_player, 
                   start_date=(datetime.date.today() - datetime.timedelta(days=1)).__str__().replace('-',''),
                   end_date=datetime.date.today().__str__().replace('-',''),
                   ret_type='arr'):
    ''' start_date: only get data between [start_date, end_date) 
    ret_type: arr|json return type
    '''
    url = 'http://lolbox.duowan.com/matchList.php'
    page = 0
    rn = 8
    # date greater than start_date, otherwise get next page
    in_date = False
    match_arr = []
    while True:
        data = {
            'serverName': p_server,
            'playerName': p_player,
            'page': page
        }
        raw_content = post(url, data)
        soup = bs4.BeautifulSoup(raw_content, from_encoding='utf-8')
        ret_cnt = 0
        for t in soup.find_all(id=re.compile('cli*')):
            t_id = t['id'].encode('utf-8').strip('cli')
            dates = t.find_all(class_=re.compile('info'))
            if len(dates) > 0:
                t_date = dates[0].get_text().encode('utf-8')
                t_date = re.search('\d\d-\d\d', t_date).group()
            else:
                t_date = '00-00'
            t_date = t_date.replace('-', '')
            # make format to yyyyMMdd
            if len(t_date) <= 4:
                t_new_date = `datetime.date.today().year` + t_date
                # e.g.: 20141211, but today is 20140312, it may be 20131211
                if t_new_date > datetime.date.today().__str__().replace('-',''):
                    t_new_date = `datetime.date.today().year-1` + t_date
                t_date = t_new_date
            if t_date < end_date:
                in_date = True
            if t_date < start_date:
                break
            # e.g.: loadMatchDetail(6348303271,'BOT','网通四','我该拿掉谁的头颅');
            t_queue = t['onclick'].encode('utf-8').split("'")[1]
            t_hero = t.img['title'].encode('utf-8')
            wins = t.find_all(class_=re.compile('green|red'))
            if len(wins) > 0:
                if wins[0].get_text() == u'胜利':
                    t_win = 1
                elif wins[0].get_text() == u'失败':
                    t_win = 0
                else:
                    t_win = -1
            t_match = {'id':t_id, 'date':t_date, 'hero':t_hero, 'win':t_win, 'queue':t_queue, 'player':p_player, 'server':p_server}
            match_arr.append(t_match)
            ret_cnt += 1
        # this page result less than rn, so current date finish
        if (in_date and ret_cnt < rn) or page >= 8:
            break
        page += 1
    if ret_type == 'arr':
        return match_arr
    elif ret_type == 'json':
        return json.dumps(match_arr, ensure_ascii=False, encoding='utf-8')
    else:
        return json.dumps(match_arr, ensure_ascii=False, encoding='utf-8')

def getMatchDetail(p_match_id, ret_type = 'arr'):
    ''' get match detail with id 
    ret_type: arr|json return type
    '''
    url = 'http://api.lolbox.duowan.com/lol/match/detail'
    data = {
        'matchId': p_match_id
    }
    raw_content = get(url, data)
    if raw_content == '':
        print "get match detail(empty) failed id[%s]" % p_match_id
        return False
    match_arr = json.loads(raw_content)
    if match_arr['code'] != '0':
        print "get match detail failed id[%s] error_code[%s]" % (p_match_id,match_arr['code'])
        return {'gameId':-1, 'player':[]}
    if ret_type == 'arr':
        return match_arr['matchDetail']
    elif ret_type == 'json':
        return json.dumps(match_arr['matchDetail'])
    else:
        return json.dumps(match_arr['matchDetail'])

def getPlayerDetail(p_server, p_player, ret_type = 'arr'):
    ''' get player detail with player name
    ret_type: arr|json return type
    '''
    url = 'http://lolbox.duowan.com/playerDetail.php'
    data = {
        'serverName': p_server,
        'playerName': p_player
    }
    raw_content = get(url, data)
    soup = bs4.BeautifulSoup(raw_content, from_encoding='utf-8')
    # @todo: extract player info, like win rate, recent hero


#if __name__ == '__main__':
    #getPlayerDetail('网通四', '我该拿掉谁的头颅')
    #getPlayerMatch('网通四', '我该拿掉谁的头颅', '20140301')
    #getMatchDetail(772317144)

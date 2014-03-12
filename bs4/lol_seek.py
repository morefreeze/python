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
    response = opener.open(req, data)
    return response.read()

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
    data = {
        'serverName': p_server,
        'playerName': p_player
    }
    raw_content = post(url, data)
    soup = bs4.BeautifulSoup(raw_content, from_encoding='utf-8')
    match_arr = []
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
            t_date = `datetime.date.today().year` + t_date
        if t_date < start_date or t_date >= end_date:
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
        'matchId':p_match_id
    }
    raw_content = get(url, data)
    match_arr = json.loads(raw_content)
    if match_arr['code'] != '0':
        print "get match detail failed id[%d]" % p_match_id
        return False
    if ret_type == 'arr':
        return match_arr['matchDetail']
    elif ret_type == 'json':
        return json.dumps(match_arr['matchDetail'])
    else:
        return json.dumps(match_arr['matchDetail'])

#if __name__ == '__main__':
    #getPlayerMatch('网通四', '我该拿掉谁的头颅', '20140309')
    #getMatchDetail(6337944362)

#!/bin/env python
# -*- coding: utf-8 -*-
''' grab lol player info from 178 API '''
import urllib
import urllib2
import bs4
import sys
import re
import json

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
    url = url + "?" + data
    return post(url, None)

def getPlayerMatch(server, player):
    ''' function main write jb comment '''
    url = 'http://lolbox.duowan.com/matchList.php'
    data = {
        'serverName': server,
        'playerName': player
    }
    raw_content = post(url, data)
    soup = bs4.BeautifulSoup(raw_content, from_encoding='utf-8')
    match_arr = []
    for t in soup.find_all(id=re.compile('cli*')):
        t_hero = t.img['title'].encode('utf-8')
        t_id = t['id'].encode('utf-8')
        wins = t.find_all(class_=re.compile('green|red'))
        if len(wins) > 0:
            if wins[0].get_text() == u'胜利':
                t_win = 1
            elif wins[0].get_text() == u'失败':
                t_win = 0
            else:
                t_win = -1
        # e.g.: loadMatchDetail(6348303271,'BOT','网通四','我该拿掉谁的头颅');
        t_mode = t['onclick'].encode('utf-8').split("'")[1]
        t_match = {'id':t_id, 'hero':t_hero, 'win':t_win, 'mode':t_mode}
        #print type(t_match['hero'])
        match_arr.append(t_match)
    print json.dumps(match_arr, ensure_ascii=False, encoding='utf-8')

if __name__ == '__main__':
    getPlayerMatch('网通四', '我该拿掉谁的头颅')

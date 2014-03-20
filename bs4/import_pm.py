#!/bin/env python
# -*- coding: utf-8 -*-
import lol_seek
import datetime
from urllib import urlencode
from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient()
    db = client.lol
    match_cnt = 0
    player_cnt = 0
    while True:
        cursor = db.match.find({'_import': None, 'serverName': {'$ne': None}}, 
                               fields = {'_id': False, 'gameId': True, 'serverName': True}).limit(1)
        # lock this data for concurrency
        ret_match = db.match.update({'gameId': cursor[0]['gameId']}, {'$set': {'_import': False}})
        if cursor.count() <= 0:
            break
        game_id = int(cursor[0]['gameId'])
        print game_id
        server_name = cursor[0]['serverName'].encode('utf-8')
        # select summoners in a game
        sum_cursor = db.match.find({'_import': None, 'summonerName': {'$ne':None}})
        for ply in sum_cursor:
            player_name = ply['summonerName'].encode('utf-8')
            # print player_name
            start_ply = lol_seek.getPlayerMatch(server_name, player_name)
            for t in start_ply:
                ret_pm = db.pm.update({'id':t['id']}, {'$set': t}, upsert=True)
                print t['id']
                if ret_pm['updatedExisting'] == False:
                    player_cnt += 1
        match_cnt += 1
        # watch out int and str of gameId
        ret_match = db.match.update({'gameId': cursor[0]['gameId']}, {'$set': {'_import': True}})
    print 'total import '+`match_cnt`+' matches '+`player_cnt`+' players'

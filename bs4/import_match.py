#!/bin/env python
# -*- coding: utf-8 -*-
import lol_seek
import datetime
import time
from urllib import urlencode
from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient()
    db = client.lol
    match_cnt = 0
    player_cnt = 0
    pm_cnt = 0
    while True:
        cursor = db.pm.find({'_import': None}, fields={'_id': False, 'id': True}, limit = 20, snapshot = True)
        # lock this data for concurrency
        t_cursor = cursor.clone()
        for t in t_cursor:
            ret_pm = db.pm.update({'id' : t['id']}, {'$set': {'_import': False}})
        if cursor.count() <= 0:
            break
        pm_cnt += cursor.count(True)
        print `pm_cnt`+'/'+`cursor.count()`
        # iterator each player match info
        for t in cursor:
            t_id = t['id'].encode('utf-8')
            print t['id']
            match_detail = lol_seek.getMatchDetail(t_id)
            if match_detail == False or len(match_detail) <= 0:
                print 'import match detail error id['+t['id']+']'
            else:
                players = match_detail['player']
                del match_detail['player']
                ret_match = db.match.update({'gameId': match_detail['gameId']}, {'$set': match_detail}, upsert = True)
                print match_detail['gameId']
                # import every player into db
                for ply in players:
                    if ply['botPlayer'] != True:
                        db.match.update({'userId': ply['userId'], 'gameId': ply['gameId']}, {'$set': ply}, upsert = True)
                        player_cnt += 1
                ret_pm = db.pm.update({'id' : t['id']}, {'$set': {'_import': True}})
                match_cnt += 1
        time.sleep(1)
    print 'total import '+`match_cnt`+' matchs, '+`player_cnt`+' players'

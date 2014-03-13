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
    pm_cnt = 0
    while True:
        cursor = db.pm.find({'_import': None}, fields={'_id': False, 'id': True}, limit = 10, snapshot = True)
        if cursor.count() <= 0:
            break
        pm_cnt += cursor.count(True)
        print `pm_cnt`+'/'+`cursor.count()`
        for t in cursor:
            match_detail = lol_seek.getMatchDetail(t['id'])
            if len(match_detail) <= 0:
                print 'import match detail error id['+t['id']+']'
                continue
            players = match_detail['player']
            del match_detail['player']
            db.match.update({'gameId': match_detail['gameId']}, match_detail, upsert = True)
            # import every player into db
            for ply in players:
                if ply['botPlayer'] != True:
                    db.match.update({'userId': ply['userId'], 'gameId': ply['gameId']}, ply, upsert = True)
                    player_cnt += 1
            ret_pm = db.pm.update({'id' : t['id']}, {'$set': {'_import': True}}, multi = True)
            print ret_pm
            match_cnt += 1
    print 'total import '+`match_cnt`+' matchs, '+`player_cnt`+' players'

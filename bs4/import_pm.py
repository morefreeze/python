#!/bin/env python
# -*- coding: utf-8 -*-
import lol_seek
import datetime
from urllib import urlencode
from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient()
    db = client.lol
    while True:
        cursor = db.player.find({'_import': None}, fields={'_id': False, 'id': True}, limit = 100, snapshot = True)
        if cursor.count() <= 0:
            break
        for t in cursor:
            match_detail = lol_seek.getMatchDetail(t['id'])
            if len(match_detail) <= 0:
                print 'import match detail error id['+t['id']+']'
                continue
            db.match.update({'gameId': match_detail['gameId']}, match_detail, upsert = True)
            # import every player into db
            for ply in match_detail['player']:
                if ply['botPlayer'] != True:
                    db.pm.update({'userId': ply['userId'], 'gameId': ply['gameId']}, ply, upsert = True)
            db.player.update({'id' : t['id']}, {'$set': {'_import': True}}, multi = True)

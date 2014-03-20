#!/bin/env python
# -*- coding: utf-8 -*-
import lol_seek
import datetime
import time
import sys
from pymongo import MongoClient

if __name__ == '__main__':
    ''' python __FILE__ [20140312]
    archive the data(imported) of pm/match/player to pm_20140312
    '''
    client = MongoClient()
    db = client.lol
    match_cnt = 0
    player_cnt = 0
    pm_cnt = 0
    if len(sys.argv) > 1:
        dt = sys.argv[1]
    else:
        dt = (datetime.date.today() - datetime.timedelta(days=1)).__str__().replace('-','')
    dt_timestamp = int(time.mktime(time.strptime(dt, "%Y%m%d")))
    dt_timestamp_end = dt_timestamp + 86400
    new_pm = 'pm_'+dt
    new_match = 'match_'+dt
    # archive pm by date
    while True:
        cursor = db.pm.find({'_import': True, 'date': dt}, limit = 1000, snapshot = True)
        if cursor.count() <= 0:
            break
        pm_cnt += cursor.count(True)
        print `pm_cnt`+'|'+`cursor.count()-cursor.count(True)`
        # iterator each player match info
        for t in cursor:
            db[new_pm].insert(t)
            db.pm.remove({'_id':t['_id']})
    # archive match by date (match end time)
    while True:
        cursor = db.match.find({'_import': True, 'endTimestamp': {'$gte': dt_timestamp, '$lt': dt_timestamp_end}}, limit = 10, snapshot = True)
        if cursor.count() <= 0:
            break
        match_cnt += cursor.count(True)
        print `match_cnt`+'|'+`cursor.count()-cursor.count(True)`
        # iterator each match info
        for t in cursor:
            game_id = int(t['gameId'])
            db[new_match].insert(t)
            db.match.remove({'_id':t['_id']})
            player_cursor = db.match.find({'gameId': game_id})
            for p_t in player_cursor:
                db[new_match].insert(p_t)
                db.match.remove({'_id':p_t['_id']})
    print `pm_cnt`+' player_matchs'+'total import '+`match_cnt`+' matches, '

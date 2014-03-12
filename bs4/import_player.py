#!/bin/env python
# -*- coding: utf-8 -*-
import lol_seek
import datetime
from urllib import urlencode
from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient()
    db = client.lol
    import_cnt = 0
    for t in start_ply:
        pm_id = db.player.update({'player':t['player'], 'id':t['id']}, t, upsert=True)
        if pm_id['updatedExisting'] == False:
            import_cnt += 1
    print 'total import '+`import_cnt`+' player'

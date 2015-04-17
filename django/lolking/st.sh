if [ -f dj.pid ];then
    ps -p $(cat dj.pid) >/dev/null 2>&1
    if [ $? -ne 0 ];then
        mv dj.log dj.log.bak
        nohup python manage.py runserver 0.0.0.0:8102 > dj.log 2>&1 &
        echo $! > dj.pid
    fi
else
    mv dj.log dj.log.bak
    nohup python manage.py runserver 0.0.0.0:8102 > dj.log 2>&1 &
    echo $! > dj.pid
fi
ps -p $(cat dj.pid)

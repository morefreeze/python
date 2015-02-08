if [ -f dj.pid ];then
    ps -p $(cat dj.pid) >/dev/null 2>&1
    if [ $? -ne 0 ];then
        mv dj.log dj.log.bak
        nohup python manage.py runserver 127.0.0.1:8002 > dj.log 2>&1 &
        echo $! > dj.pid
        sleep 1
    fi
else
    mv dj.log dj.log.bak
    nohup python manage.py runserver 127.0.0.1:8002 > dj.log 2>&1 &
    echo $! > dj.pid
    sleep 1
fi
tail dj.log
ps -p $(cat dj.pid)

if [ -f dj.pid ];then
    ps -p $(cat dj.pid)
    if [ $? -ne 0 ];then
        mv dj.log dj.log.bak
        nohup python manage.py runserver 127.0.0.1:8002 > dj.log 2>&1 &
        echo $! > dj.pid
    fi
else
    mv dj.log dj.log.bak
    nohup python manage.py runserver 127.0.0.1:8002 > dj.log 2>&1 &
    echo $! > dj.pid
fi

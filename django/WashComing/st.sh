if [ -f dj.pid ];then
    ps -p $(cat dj.pid)
    if [ $? -ne 0 ];then
        rm nohup.out 1>&2
        nohup python manage.py runserver 0.0.0.0:8002 > dj.log &
        echo $! > dj.pid
    fi
else
    rm nohup.out 1>&2
    nohup python manage.py runserver 0.0.0.0:8002 > dj.log &
    echo $! > dj.pid
fi

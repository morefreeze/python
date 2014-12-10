rm nohup.out 1>&2
nohup python manage.py runserver 0.0.0.0:8002 > dj.log &
echo $! > dj.pid

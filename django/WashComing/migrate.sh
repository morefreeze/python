echo $#
if [ $# -gt 0 ];then
    python manage.py makemigrations $1
    python manage.py migrate $1
else
    echo sh $0 app
fi

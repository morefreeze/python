if [ $# -lt 1 ];then
    echo sh $0 app_name
    exit 1
fi
mkdir -p $1
for i in __init__.py admin.py forms.py models.py serializers.py urls.py views.py; do
    cp WCUser/$i $1/
    sed "s/\bUser\b/$1/g" -i $1/$i
done
sed "s/\bfo_user\b/fo_$1/g" -i $1/views.py
sed "s/\bmo_user\b/mo_$1/g" -i $1/views.py

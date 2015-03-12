if [ $# -lt 1 ];then
    echo sh $0 app_name
    exit 1
fi
mkdir -p $1
for i in forms.py models.py serializers.py urls.py views.py; do
    cp WCUser/$i $1/
    sed 's/User/Cloth/g' -i $1/$i
done
sed 's/fo_user/fo_cloth/g' -i $1/views.py

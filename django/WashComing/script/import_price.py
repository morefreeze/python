import base
from WCCloth.models import Cloth

f = open('../1.txt', 'r')
for l in f:
    l = l.strip()
    [name, pr] = l.split(' ')
    print name,pr
    try:
        mo_c = Cloth.objects.get(name=name)
    except Cloth.DoesNotExist as e:
        print '*'*20,name
        continue
    mo_c.price = pr
    mo_c.save()

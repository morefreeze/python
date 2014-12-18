import base
import os
import django

import os, uuid, hashlib
from WCCloth.models import Cloth
os.chdir('/home/wwwroot/default/media/clothes')
for (dirpath, dirnames, filenames) in os.walk('.'):
    for filename in filenames:
        i_cid = os.path.splitext(filename)[0]
        if len(i_cid) > 20:
            continue
        try:
            mo_cloth = Cloth.objects.get(name=i_cid)
        except (Cloth.DoesNotExist) as e:
            print i_cid
            continue
        new_name = hashlib.md5(uuid.uuid4().__str__()).hexdigest()
        os.rename(filename, new_name+'.png')
        mo_cloth.image = 'clothes/'+new_name+'.png'
        mo_cloth.save()


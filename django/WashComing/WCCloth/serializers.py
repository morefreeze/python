from rest_framework import serializers
from WCCloth.models import Cloth

class ClothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloth
        fields = ('cid', 'is_leaf', 'fa_cid', 'name', 'detail', 'price', 'ext')

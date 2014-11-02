from rest_framework import serializers
from WCUser.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uid', 'name', 'token', 'last_time', 'score', 'exp', 'phone', 'email')

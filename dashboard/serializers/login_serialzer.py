from rest_framework import serializers
from ..models import CustomerUser

class RegSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
    )

    class Meta:
        model = CustomerUser
        fields = ['id', 'first_name', 'last_name','username', 'password',]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomerUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

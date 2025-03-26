from rest_framework import serializers
from userManagement.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "age"]
        read_only_fields = ["id"]
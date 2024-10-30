from rest_framework import serializers
from reviews.models import User


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "bio", "role"]
        read_only_fields = ["role"]

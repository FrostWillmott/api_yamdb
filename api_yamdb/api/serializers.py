from django.core.validators import EmailValidator, RegexValidator
from rest_framework import serializers
from reviews.models import User


class SignupSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(
    #     validators=[
    #         MinLengthValidator(3),
    #         MaxLengthValidator(150),
    #         RegexValidator(
    #             regex=r'^[\w.@+-]+$',
    #             message='Username must contain only letters, numbers, and @/./+/-/_ characters.'
    #         )
    #     ]
    # )
    # email = serializers.EmailField(
    #     validators=[
    #         MaxLengthValidator(254)
    #     ]
    # )

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
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        ]


class UserProfileSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ["role"]

from django.core.validators import RegexValidator, MinLengthValidator, \
    MaxLengthValidator
from rest_framework import serializers

from reviews.models import User


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
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
    # first_name = serializers.CharField(
    #     validators=[
    #         MaxLengthValidator(30)
    #     ]
    # )
    # last_name = serializers.CharField(
    #     validators=[
    #         MaxLengthValidator(150)
    #     ]
    # )
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'role']
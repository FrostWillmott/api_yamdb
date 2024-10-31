import string
import random

from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import serializers, status
from reviews.models import User


# FIX. Достаточно будет смертного сериалайзера
# serializers.Serializer
# class SignupSerializer(serializers.ModelSerializer):
class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(required=True, max_length=128)

    # FIX. Для смертного сериалайзера не нужно Meta.
    # class Meta:
    #     model = User
    #     fields = ["username", "email"]

    # FIX. Не нужно, это сделается по умолчанию.
    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     return user

    def validate_username(self, value):
        # TODO
        pass

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"],
                               username=attrs["username"]).exists():
            return attrs

            # Это во view
            # confirmation_code = "".join(
            #     random.choices(string.ascii_uppercase + string.digits, k=6))
            # attrs["confirmation_code"] = confirmation_code
            # user = User(**attrs)
            # user.save()
            # send_mail(
            #     "Ваш код подтверждения",
            #     f"Ваш код подтверждения: {confirmation_code}",
            #     "from@example.com",
            #     [attrs["email"]],
            #     fail_silently=False,
            # )
            # return attrs

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует")
        return attrs


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "bio", "role"]
        read_only_fields = ["role"]

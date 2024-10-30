from rest_framework import serializers
from reviews.models import User


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email"]
        extra_kwargs = {
            "username": {"validators": User.username.field.validators},
            "email": {"validators": User.email.field.validators},
        }

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        return user

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")

        if username.lower() == "me":
            raise serializers.ValidationError('Username "me" запрещен')

        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            if existing_user.email == email:
                return attrs
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует"
            )

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email уже зарегистрирован")

        return attrs


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

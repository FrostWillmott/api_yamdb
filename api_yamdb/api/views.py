import random
import string

from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import User

from api.permissions import IsAdmin
from api.serializers import SignupSerializer, TokenSerializer, UserSerializer


class SignupViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer



    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]

        if username.lower() == "me":
            raise ValidationError(
                {"username": 'Имя пользователя "me" запрещено.'})
        if User.objects.filter(email=email).exclude(pk=self.request.user.pk).exists():
            return Response({"email": "Этот email уже зарегистрирован."},
                            status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(username=username, email=email)
        confirmation_code = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6))
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            "Ваш код подтверждения",
            f"Ваш код подтверждения: {confirmation_code}",
            "from@example.com",
            [user.email],
            fail_silently=False,
        )
        return Response({"email": user.email, "username": user.username},
                        status=status.HTTP_200_OK)

class TokenViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(
                username=serializer.validated_data["username"],
            )
            if user.confirmation_code != serializer.validated_data["confirmation_code"]:
                return Response({"detail": "Неверный код подтверждения."},
                                status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        refresh = RefreshToken.for_user(user)
        return Response({"token": str(refresh.access_token)}, status=status.HTTP_200_OK)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = "username"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["username"]
    search_fields = ["username"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        if User.objects.filter(email=email).exists():
            return Response({"email": "Этот email уже зарегистрирован."},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

import random
import string

from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import ROLE_CHOICES, User

from api.permissions import IsAdmin
from api.serializers import SignupSerializer, TokenSerializer, UserSerializer


class SignupViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]
        # FIX. Валидацию в сералайзер.
        # if username.lower() == "me":
        #     raise ValidationError(
        #         {"username": 'Имя пользователя "me" запрещено.'})
        user, created = User.objects.get_or_create(username=username, email=email)

        # FIX. Логику для confirmation_code нужно рефакторить.
        # См. сообщение в канале.
        # confirmation_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        # user.confirmation_code = confirmation_code
        # user.save()

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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = "username"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["username"]
    search_fields = ["username"]
    pagination_class = PageNumberPagination

    http_method_names = ["get", "post", "patch", "delete"]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                {"email": "Пользователь с таким e-mail уже существует."})

        super().create(request, *args, **kwargs)
        user = User.objects.get(email=email)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get", "patch"],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        # if request.method == "GET":
        #     serializer = self.get_serializer(request.user)
        #     return Response(serializer.data,  status=status.HTTP_200_OK)
        if request.method == "PATCH":
            # data = request.data
            # if "role" in data and data["role"] not in ROLE_CHOICES:
            #     return Response({"detail": "Invalid role."},
            #                     status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(self.request.user, data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

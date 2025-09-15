from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.authentication.serializers import UserReadSerializer, UserWriteSerializer
from utils.envelope import Envelope


class SignUpView(APIView):
    def post(self, request):
        serializer = UserWriteSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Envelope.success_response(
                data=UserReadSerializer(user).data,
                status_code=status.HTTP_201_CREATED,
            )
        else:
            return Envelope.error_response(
                error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e
        return Envelope.success_response(data=serializer.validated_data)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserReadSerializer(request.user)
        return Envelope.success_response(serializer.data)

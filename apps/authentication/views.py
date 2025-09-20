from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.authentication.serializers import (
    ProfileReadSerializer,
    ProfileWriteSerializer,
    UserReadSerializer,
    UserWriteSerializer,
    VerificationTokenSerializer,
)
from apps.authentication.tasks import send_verification_email
from utils.envelope import Envelope
from utils.tokens import create_email_verification_token


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

    def patch(self, request):
        first_name = request.user.first_name
        last_name = request.user.last_name
        data = {
            "first_name": request.data.get("first_name", first_name),
            "last_name": request.data.get("last_name", last_name),
        }
        serializer = UserWriteSerializer(request.user, data=data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Envelope.success_response(UserReadSerializer(user).data)
        return Envelope.error_response(
            error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileReadSerializer(request.user.profile)
        return Envelope.success_response(data=serializer.data)

    def patch(self, request):
        serializer = ProfileWriteSerializer(
            request.user.profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            profile = serializer.save()
            return Envelope.success_response(ProfileReadSerializer(profile).data)
        return Envelope.error_response(
            error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )


class VerifyEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.email_verified:
            return Envelope.success_response("email already verified")

        serializer = VerificationTokenSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Envelope.success_response("email verified")
        else:
            return Envelope.error_response(
                error=serializer.errors, status_code=status.HTTP_401_UNAUTHORIZED
            )


class SendEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.email_verified:
            return Envelope.success_response("email already verified")
        verification_token = create_email_verification_token(request.user)
        send_verification_email.delay(
            first_name=request.user.first_name,
            email=request.user.email,
            token=verification_token.token,
        )
        return Envelope.success_response(
            data="email sent", status_code=status.HTTP_202_ACCEPTED
        )

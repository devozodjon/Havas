from rest_framework import status, generics
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser, VerificationCode
from apps.users.serializers import RegisterSerializer, LoginSerializer, ProfileRetrieveSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'detail': 'Verification code sent to email'}, status=status.HTTP_201_CREATED)


class VerifyEmailAPIView(generics.GenericAPIView):
    @staticmethod
    def post(request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)

        try:
            verification = VerificationCode.objects.filter(user=user, code=code, used=False).latest('created_at')
        except VerificationCode.DoesNotExist:
            return Response({'error': 'Invalid or expired code'}, status=400)

        if not verification.is_valid():
            return Response({'error': 'Code expired'}, status=400)

        user.is_active = True
        user.save()
        verification.used = True
        verification.save()

        return Response({'detail': 'Email verified successfully.'})



class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            return Response(tokens, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileRetrieveSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
import json
import time
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from pdx_auth.exceptions import InvalidCurrentPassword, UserNotFound
from django.http import HttpResponse
from oauth2_provider.views.base import TokenView
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.models import get_access_token_model
from oauth2_provider.signals import app_authorized
from pdx_auth.models import ConnectedApplication, PDXUser
from pdx_auth.utils import (
    generate_OTP,
    get_organization_data,
    send_otp,
)
from pdx_auth_gateway.utils import get_username
from .serializers import (
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UpdatePasswordSerializer,
    CreateUserSerializer,
    SetPasswordSerializer,
    CallbackURISerializer,
)
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from oauth2_provider.models import Application


class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer


class SetPassword(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            email = validated_data["email"]
            password = validated_data["password"]

            org_name = get_organization_data(request)

            try:
                register_obj = PDXUser.objects.get(
                    username=get_username(email, org_name)
                )
            except PDXUser.DoesNotExist:
                raise UserNotFound()

            register_obj.set_password(password)
            register_obj.save()

            return Response(
                {"message": "Set password successfully!"}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(APIView):
    def post(self, request):
        org_name = get_organization_data(request)
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data

            try:
                user_obj = PDXUser.objects.get(
                    username=get_username(
                        validated_data["email"],
                        org_name,
                    )
                )
            except PDXUser.DoesNotExist:
                raise UserNotFound()

            otp = generate_OTP()
            user_obj.otp = int(otp)
            user_obj.save()

            send_otp(user_obj, org_name)
            response = {
                "message": "Please check your mail box.",
                "data": {"id": user_obj.id, "email": user_obj.email},
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=400)


class ResetPassword(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            email = validated_data["email"]
            password = validated_data["password"]
            requested_otp = validated_data["otp"]
            username = get_username(email, get_organization_data(request))

            try:
                user_obj = PDXUser.objects.get(username=username)
            except PDXUser.DoesNotExist:
                raise UserNotFound()
            if user_obj.otp == int(requested_otp):
                user_obj.set_password(password)
                user_obj.save()
                return Response(
                    {"message": "Set password successfully!"}, status=status.HTTP_200_OK
                )

            return Response(
                {"message": "Please check your OTP!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePassword(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdatePasswordSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            current_password = serializer.validated_data["current_password"]
            new_password = serializer.validated_data["new_password"]

            if not user.check_password(current_password):
                raise InvalidCurrentPassword()

            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password updated successfully."}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateBulkUsers(APIView):
    def post(self, request, *args, **kwargs):
        user_data = request.data.get("user_data")
        for data in user_data:
            username = data["username"]
            data.pop("username")
            obj, created = PDXUser.objects.update_or_create(
                username=username, defaults={**data}
            )
            print(f"{obj.username} is created") if created else print(
                f"{obj.username} is updated"
            )
        return Response({"message": "user migration completed"})


class CustomTokenView(TokenView):
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        url, headers, body, status = self.create_token_response(request)
        if status == 200:
            body = json.loads(body)
            access_token = body.get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(token=access_token)
                app_authorized.send(sender=self, request=request, token=token)
                body["data"] = {
                    "id": str(token.user.id),
                    "first_name": token.user.first_name,
                    "last_name": token.user.last_name,
                    "email": token.user.email,
                }
                body = json.dumps(body)
        response = HttpResponse(content=body, status=status)
        for k, v in headers.items():
            response[k] = v
        return response


class CustomTokenRefreshView(TokenView):
    def post(self, request, *args, **kwargs):
        url, headers, body, status = self.create_token_response(request)
        if status == 200:
            body = json.loads(body)
            access_token = body.get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(token=access_token)
                app_authorized.send(sender=self, request=request, token=token)
                body["data"] = {
                    "id": str(token.user.id),
                    "first_name": token.user.first_name,
                    "last_name": token.user.last_name,
                    "email": token.user.email,
                }
                body = json.dumps(body)
        response = HttpResponse(content=body, status=status)
        for k, v in headers.items():
            response[k] = v
        return response


class LogoutAPIView(APIView):
    def delete(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})


class CallbackURIRetrieveView(generics.RetrieveAPIView):
    queryset = Application.objects.all()
    serializer_class = CallbackURISerializer
    lookup_field = "client_id"


class CallbackURIUpdateView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = CallbackURISerializer
    lookup_field = "client_id"


class ValidateConnectedApplication(APIView):
    """ Validates if there is a connected brige between two applications.
        Expects server to server call """

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        from_application_client_id = payload.get("from_application_client_id")
        to_application_client_id = payload.get("to_application_client_id")

        if not all([from_application_client_id, to_application_client_id]):
            return Response({ "is_connected": False })
        
        from_application = ConnectedApplication.objects.filter(
            to_application__client_id=to_application_client_id,
            from_application__client_id=from_application_client_id
        )
        return Response({ "is_connected": from_application.exists() })


class OTPGenerationForUser(APIView):
    """ A view which is used for OTP generation for a user """

    def get(self, request, *args, **kwargs):
        """ OTP getter view expectes user_email and org_name as mandatory parameters """

        payload = request.GET.dict()
        user_email = payload.get("email")
        org_name = payload.get("org_name")

        if not all([user_email, org_name]):
            return Response(
                {"message": "email and org_name are mandatory parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user = PDXUser.objects.get(username=get_username(user_email, org_name))
        otp = generate_OTP()
        user.otp = int(otp)
        user.otp_generated_at = int(time.time())
        user.save()
        return Response({
            "otp": otp,
            "message": "OTP generated successfully"
        })


class ValidateOTPForUser(APIView):
    """ Endpoint to validate OTP for a user """

    def get(self, request, *args, **kwargs):
        """ OTP validation view expects user_email, org_name and otp as mandatory parameters """

        payload = request.GET.dict()
        user_email = payload.get("email")
        org_name = payload.get("org_name")
        otp = payload.get("otp")

        if not all([user_email, org_name, otp]):
            return Response(
                {"message": "email, org_name and otp are mandatory parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = PDXUser.objects.get(username=get_username(user_email, org_name))
        is_expired, is_verified, message = user.validate_otp(otp=otp)
        return Response({
            "message": message,
            "is_expired": is_expired,
            "is_verified": is_verified,
        }, status=status.HTTP_200_OK if is_verified else status.HTTP_400_BAD_REQUEST)

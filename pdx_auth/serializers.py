from rest_framework import serializers

from pdx_auth.exceptions import PasswordDidnotMatch
from .models import PDXUser
from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import validate_password
from oauth2_provider.models import Application


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDXUser
        fields = ["username", "first_name", "last_name", "password", "email"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = PDXUser.objects.create_user(**validated_data)
        return user


class SetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField()

    class Meta:
        model = PDXUser
        fields = ("email", "password", "confirm_password")

    def validate_password(self, value):
        user = PDXUser(username="temp")  # Creating a temporary user object
        password_validation.validate_password(value, user)
        return value

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise PasswordDidnotMatch()

        return data


class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDXUser
        fields = ("email",)


class ResetPasswordSerializer(serializers.ModelSerializer):
    otp = serializers.IntegerField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        user = PDXUser(username="temp")  # Creating a temporary user object
        password_validation.validate_password(value, user)
        return value

    class Meta:
        model = PDXUser
        fields = ("email", "password", "otp")


class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_new_password(self, value):
        # Use Django's built-in password validation to ensure the new password is strong enough.
        validate_password(value)
        return value

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if new_password != confirm_password:
            raise PasswordDidnotMatch()

        return data


class CallbackURISerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["client_id", "redirect_uris"]
        read_only_fields = ["client_id"]

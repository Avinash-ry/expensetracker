import time
import uuid
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.db import models

from oauth2_provider.models import Application


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        if not first_name:
            raise ValueError("The First Name field must be set")
        if not last_name:
            raise ValueError("The Last Name field must be set")

        email = self.normalize_email(email)
        user = self.model(
            email=email, username=username, first_name=first_name, last_name=last_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None):
        user = self.create_user(email, username, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class PDXUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    otp = models.IntegerField(null=True, blank=True)
    otp_generated_at = models.BigIntegerField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.username
    
    def validate_otp(self, otp):
        """ A model method which handles otp validation for the user """
        if (int(time.time()) - self.otp_generated_at) >= settings.USER_OTP_VALID_DURATION_SECONDS:
            return (True, False, "OTP has expired!")

        if self.otp != int(otp):
            return (False, False, "OTP validation failed!")

        return (False, True, "OTP validated successfully!")


class ConnectedApplication(models.Model):
    """ A model which establishes linking between multiple applications """
    from_application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='from_app')
    to_application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='to_app')

    def __str__(self):
        return f'{self.from_application} -> {self.to_application}'

from django.db import models

class Transaction(models.Model):
    transaction_date = models.DateField(verbose_name="Transaction Date")
    description = models.TextField(verbose_name="Description")
    ref_number = models.CharField(max_length=255, verbose_name="Reference Number")
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Debit Amount", null=True, blank=True)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Credit Amount", null=True, blank=True)
    account = models.CharField(max_length=255, verbose_name="Account")

    def __str__(self):
        return f"{self.description} - {self.ref_number}"

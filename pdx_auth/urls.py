from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *
from .apis import *


app_name = "pdx_auth"
urlpatterns = [
    path("create-user/", CreateUserView.as_view()),
    path("set-password/", SetPassword.as_view()),
    path("forgot-password/", ForgotPassword.as_view()),
    path("reset-password/", ResetPassword.as_view()),
    path("user-details/update-password/", UpdatePassword.as_view()),
    path("user-bulk-create/", CreateBulkUsers.as_view()),
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("create-token/", CustomTokenView.as_view()),
    path("refresh-token/", CustomTokenRefreshView.as_view()),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path(
        "update-callback-uri/<str:client_id>/",
        CallbackURIUpdateView.as_view(),
        name="update-callback-uri",
    ),
    path(
        "retrieve-callback-uri/<str:client_id>/",
        CallbackURIRetrieveView.as_view(),
        name="retrieve-callback-uri",
    ),
    path("authorize/", CustomAuthorizationView.as_view(), name="authorize"),
    path("force-logout/", CustomLogoutView.as_view(), name="force-logout"),
    path(
        "validate-connected-applications/",
        ValidateConnectedApplication.as_view(),
        name="validate-connected-applications"
    ),
    path("generate-otp-for-user/", OTPGenerationForUser.as_view(), name="generate_otp_for_user"),
    path("validate-otp-for-user/", ValidateOTPForUser.as_view(), name="validate_otp_for_user"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

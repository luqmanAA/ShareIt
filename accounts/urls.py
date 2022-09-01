from django.urls import path
from .views import (
    RegisterUserView,
    ActivateUserView,
    UserLoginView,
    ForgotPasswordView,
    PasswordResetValidateView,
    PasswordResetView,
    LogOutView,
    DashboardView,
    ProfileEditView,
    UserProfileView,
    ChangePasswordView,
)

app_name = "accounts"
urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogOutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("edit_profile/", ProfileEditView.as_view(), name="edit_profile"),
    path("user_profile/<int:pk>", UserProfileView.as_view(), name="profile_view"),

    path("activate/<uidb64>/<token>/", ActivateUserView.as_view(), name="activate"),
    path("forgotPassword/", ForgotPasswordView.as_view(), name="forgotPassword"),
    path("resetpassword_validate/<uidb64>/<token>/", PasswordResetValidateView.as_view(),
         name="resetpassword_validate"),
    path("resetPassword/", PasswordResetView.as_view(), name="resetPassword"),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
]

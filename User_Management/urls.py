from django.urls import path

from User_Management.Views.LoginView import LoginView, VerifyTokenView
from User_Management.Views.LogoutView import LogoutView
from User_Management.Views.MemberSignupView import MemberSignupView
from User_Management.Views.MembersView import MembersView, MemberView
from User_Management.Views.StaffsView import StaffsView, StaffView
from User_Management.Views.SuppliersView import (
    SupplierApplyView,
    SupplierStatusView,
    HideSupplierView,
    SupplierDetailView,
    SupplierInterviewView,
    DeclineSupplierView,
    ApproveSupplierView,
    ContractUploadSupplierView,
    ContractUpdateSupplierView,
)
from User_Management.Views.UserForgotPasswordView import (
    UserForgotPasswordView,
    UserVerifyOTPView,
    UserResetPasswordView,
)
from User_Management.Views.UserPasswordView import UserPasswordView
from User_Management.Views.UserProfileDeleteView import UserProfileDeleteView, UserProfileVerifyDeletionView
from User_Management.Views.UserProfileView import UserProfileView
from User_Management.Views.VerifyMemberSignUpView import VerifyMemberSignUpView


urlpatterns = [
    # Token Verification
    path("token/verify", VerifyTokenView.as_view()),
    # Manage Authentication
    path("auth/login/", LoginView.as_view()),
    path("auth/signup/", MemberSignupView.as_view()),
    # Manage Verification
    path("auth/verify-signup/", VerifyMemberSignUpView.as_view()),
    # Manage Reset Password
    path("auth/forgot-password/", UserForgotPasswordView.as_view()),
    path("auth/verify-otp/", UserVerifyOTPView.as_view()),
    path("auth/reset-password/", UserResetPasswordView.as_view()),
    # Manage Members
    path("members/", MembersView.as_view()),
    path("member/", MemberView.as_view()),
    # Manage Staff
    path("staffs/", StaffsView.as_view()),
    path("staff/", StaffView.as_view()),
    # Manage Suppliers
    path("supplier/apply/", SupplierApplyView.as_view()),
    path("supplier/details/", SupplierDetailView.as_view()),
    path("supplier/interview/", SupplierInterviewView.as_view()),
    path("supplier/status/", SupplierStatusView.as_view()),
    path("supplier/hide/", HideSupplierView.as_view()),
    path("supplier/approve/", ApproveSupplierView.as_view()),
    path("supplier/decline/", DeclineSupplierView.as_view()),
    path("supplier/contract/upload", ContractUploadSupplierView.as_view()),
    path("supplier/contract/update", ContractUpdateSupplierView.as_view()),
    # Manage Profile
    path('user/profile/', UserProfileView.as_view()),
    path("user/logout/", LogoutView.as_view()),
    # Manage Update Password
    path("user/password/", UserPasswordView.as_view()),
    # Mange Account Deletion
    path('account/delete', UserProfileDeleteView.as_view()),
    path('account/delete/verify', UserProfileVerifyDeletionView.as_view()),
     
]

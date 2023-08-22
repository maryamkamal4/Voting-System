from django.urls import path
from .views import SignUpView, CustomLoginView, AdminApprovalView, UserEmailConfirmationView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('admin-approval/', AdminApprovalView.as_view(), name='admin-approval'),
    path('verify/<str:uidb64>/<str:token>/', UserEmailConfirmationView.as_view(), name='email-confirmation'),
]
from django.urls import path
from .views import ActivateUserView, ApproveUserView, SignUpView, CustomLoginView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('approve-user/<int:pk>', ApproveUserView.as_view(), name='approve-user'),
    path('activate/<str:uidb64>/<str:token>/', ActivateUserView.as_view(), name='activate-user'),
]
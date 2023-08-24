from django.urls import path
from .views import ActivateUserView, ApproveUserView, CustomLogoutView, SignUpView, CustomLoginView, SuperuserDashboardView, VoterDashboardView, halka_addition

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='custom_logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('approve-user/<int:pk>', ApproveUserView.as_view(), name='approve-user'),
    path('activate/<str:uidb64>/<str:token>/', ActivateUserView.as_view(), name='activate-user'),
    path('halka/add/', halka_addition, name='halka-addition'),
    path('dashboard/superuser/', SuperuserDashboardView.as_view(), name='superuser-dashboard'),
    path('dashboard/voter/', VoterDashboardView.as_view(), name='voter-dashboard'),
]
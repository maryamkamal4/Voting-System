from django.urls import path
from account.views import SignUpView, CustomLoginView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
]

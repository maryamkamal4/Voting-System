from django.contrib import admin
from django.urls import include, path
from account.views import CustomLoginView

urlpatterns = [
    # Custom URLs
    path('', CustomLoginView.as_view(), name='login'),
    path('account/', include('account.urls')),
    path('voting/', include('voting.urls')),
    path('admin/', admin.site.urls),
]

# Custom 404 handler
handler404 = 'account.views.handler404'

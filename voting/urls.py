from django.urls import path
from .views import BecomeCandidateView, CandidateApplicationListView

urlpatterns = [
    path('candidate-applications/', CandidateApplicationListView.as_view(), name='candidate-application-list'),
    path('become-candidate/', BecomeCandidateView.as_view(), name='become-candidate'),
]
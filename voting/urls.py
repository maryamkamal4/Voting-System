from django.urls import path
from .views import BecomeCandidateView, CandidateApplicationListView, CandidateApplicationUpdateView

urlpatterns = [
    path('candidate-applications/', CandidateApplicationListView.as_view(), name='candidate-application-list'),
    path('candidate-application/<int:pk>/', CandidateApplicationUpdateView.as_view(), name='candidate-application-update'),
    path('become-candidate/', BecomeCandidateView.as_view(), name='become-candidate'),
]
from django.urls import path
from .views import BecomeCandidateView, CandidateApplicationListView, CandidateResultsView, SetPollingScheduleView, VoteView

urlpatterns = [
    path('candidate-applications/', CandidateApplicationListView.as_view(), name='candidate-application-list'),
    path('become-candidate/', BecomeCandidateView.as_view(), name='become-candidate'),
    path('vote/', VoteView.as_view(), name='vote'),
    path('candidate/results/', CandidateResultsView.as_view(), name='candidate-results'),
    path('admin/set-polling-schedule/', SetPollingScheduleView.as_view(), name='set-polling-schedule'),
]
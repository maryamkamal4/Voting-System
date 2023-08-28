from django.urls import path
from .views import BecomeCandidateView, CandidateApplicationListView, CandidateTotalVotesView, PollingScheduleView, VoteCastedMultipleTimesView, VoteCastedSuccessView, VoteView

urlpatterns = [
    path('candidate-applications/', CandidateApplicationListView.as_view(), name='candidate-application-list'),
    path('become-candidate/', BecomeCandidateView.as_view(), name='become-candidate'),
    path('vote/', VoteView.as_view(), name='vote'),
    path('vote-cast-success/', VoteCastedSuccessView.as_view(), name='vote-cast-success'),
    path('vote-cast-multiple-times/', VoteCastedMultipleTimesView.as_view(), name='vote-cast-multiple-times'),
    path('set-polling-schedule/', PollingScheduleView.as_view(), name='set-polling-schedule'),
    path('candidate-total-votes/', CandidateTotalVotesView.as_view(), name='candidate-total-votes'),
]
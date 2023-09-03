from django.urls import path
from .views import BecomeCandidateView, CandidateApplicationListView, CandidateListView, CandidateProfilesView, CandidateTotalVotesView, PollingScheduleView, PreviousPollingScheduleListView, VoteCastedMultipleTimesView, VoteCastedSuccessView, VoteView, VotersListView

urlpatterns = [
    path('candidate-applications/', CandidateApplicationListView.as_view(), name='candidate-application-list'),
    path('become-candidate/', BecomeCandidateView.as_view(), name='become-candidate'),
    path('vote/', VoteView.as_view(), name='vote'),
    path('vote-cast-success/', VoteCastedSuccessView.as_view(), name='vote-cast-success'),
    path('vote-cast-multiple-times/', VoteCastedMultipleTimesView.as_view(), name='vote-cast-multiple-times'),
    path('set-polling-schedule/', PollingScheduleView.as_view(), name='set-polling-schedule'),
    path('candidate-total-votes/', CandidateTotalVotesView.as_view(), name='candidate-total-votes'),
    path('candidate-profiles/', CandidateProfilesView.as_view(), name='candidate-profiles'),
    path('candidate/voters/', VotersListView.as_view(), name='voters-list'),
    path('previous-polling-schedules/',PreviousPollingScheduleListView.as_view(), name='previous_polling_schedules'),
    path('all_candidates/', CandidateListView.as_view(), name='all-candidates'),

]
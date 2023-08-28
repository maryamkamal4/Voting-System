from click import Group
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from FinalProject import settings
from account.models import CustomUser
from voting.models import CandidateApplication, PollingSchedule, Vote
from .forms import CandidateApplicationForm, PollingScheduleForm, VoteForm
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.contrib.auth import logout
from click import Group
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from FinalProject import settings
from voting.models import CandidateApplication
from .forms import CandidateApplicationForm
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
import pdb


class BecomeCandidateView(LoginRequiredMixin, FormView):
    template_name = 'become_candidate.html'
    form_class = CandidateApplicationForm
    success_url = '/'  # Change this to the appropriate URL

    def form_valid(self, form):
        application = form.save(user=self.request.user, commit=False)
        application.save()

        # Change user's is_active to False
        self.request.user.is_active = False
        self.request.user.save()

        # Log out the user
        logout(self.request)

        return super().form_valid(form)


class CandidateApplicationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'candidate_application_list.html'
    model = CandidateApplication
    context_object_name = 'applications'

    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()

    def post(self, request, *args, **kwargs):
        if 'accept_application' in request.POST:
            application_id = request.POST.get('accept_application')
            try:
                application = CandidateApplication.objects.get(pk=application_id)
                user = application.user

                # Remove user from the 'voter' group
                voter_group = Group.objects.get(name='voter')
                user.groups.remove(voter_group)

                # Add user to the 'candidate' group
                candidate_group = Group.objects.get(name='candidate')
                user.groups.add(candidate_group)

                # Change user's is_active to True
                user.is_active = True
                user.save()

                # Send email to the user
                send_mail(
                    subject=_('Candidacy Application Approved'),
                    message=_('Congratulations! Your candidacy application has been approved.'),
                    from_email=settings.EMAIL_HOST_USER,  # Use your sender email here
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                # Delete the CandidateApplication instance
                application.delete()

                messages.success(request, 'Application accepted and user promoted to candidate.')
            except CandidateApplication.DoesNotExist:
                messages.error(request, 'Error while accepting application.')

        return self.get(request, *args, **kwargs)

# class VoteView(LoginRequiredMixin, FormView):
#     template_name = 'vote.html'
#     form_class = VoteForm
#     success_url = '/dashboard/voter/'  # Redirect to voter dashboard after voting

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_halka'] = self.request.user.halka
#         return kwargs

#     def form_valid(self, form):
#         candidate = form.cleaned_data['candidate']
#         voter = self.request.user
#         halka = voter.halka

#         # Check if the voter has already cast a vote in this halka
#         if Vote.objects.filter(voter=voter, halka=halka).exists():
#             return redirect('voter-dashboard')  # Redirect with a message that vote already cast
        
#         # Create a new Vote instance
#         vote = Vote(voter=voter, candidate=candidate, halka=halka)
#         vote.save()

#         return super().form_valid(form)

# class VoteView(LoginRequiredMixin, FormView):
#     template_name = 'vote.html'
#     form_class = VoteForm
#     success_url = '/dashboard/voter/'  # Redirect to voter dashboard after voting

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_halka'] = self.request.user.halka
#         return kwargs

#     def form_valid(self, form):
#         candidate = form.cleaned_data['candidate']
#         voter = self.request.user
#         halka = voter.halka

#         # Check if the voter has already cast a vote in this halka
#         if Vote.objects.filter(voter=voter, halka=halka).exists():
#             return redirect('vote-cast-multiple-times')
        
#         # Create a new Vote instance
#         vote = Vote(voter=voter, candidate=candidate, halka=halka)
#         vote.save()

#         return redirect('vote-cast-success')

class VoteView(LoginRequiredMixin, FormView):
    template_name = 'vote.html'
    form_class = VoteForm
    success_url = '/dashboard/voter/'  # Redirect to voter dashboard after voting

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            polling_schedule = PollingSchedule.objects.latest('start_datetime')
            context['voting_open'] = polling_schedule.is_voting_open()
            context['polling_schedule'] = polling_schedule
            print("Voting Open:", context['voting_open'])
            print("Start Datetime:", polling_schedule.start_datetime)
            print("End Datetime:", polling_schedule.end_datetime)
        except PollingSchedule.DoesNotExist:
            context['voting_open'] = False
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_halka'] = self.request.user.halka
        return kwargs

    def form_valid(self, form):
        candidate = form.cleaned_data['candidate']
        voter = self.request.user
        halka = voter.halka

        # Check if the voter has already cast a vote in this halka
        if Vote.objects.filter(voter=voter, halka=halka).exists():
            return redirect('vote-cast-multiple-times')
            
        # Create a new Vote instance
        vote = Vote(voter=voter, candidate=candidate, halka=halka)
        vote.save()

        return redirect('vote-cast-success')

class VoteCastedSuccessView(TemplateView):
    template_name = 'vote_casted_success.html'

class VoteCastedMultipleTimesView(TemplateView):
    template_name = 'vote_casted_multiple.html'


class PollingScheduleView(UserPassesTestMixin, FormView):
    template_name = 'set_polling_schedule.html'
    form_class = PollingScheduleForm
    success_url = '/'  # Change this to the appropriate URL

    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

from datetime import datetime
from click import Group
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
import pytz
from FinalProject import settings
from voting.models import Candidate, CandidateApplication, Party, PollingSchedule, Vote
from .forms import CandidateApplicationForm, PollingScheduleForm, VoteForm
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
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
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from account.models import CustomUser

@method_decorator(login_required, name='dispatch')
class BecomeCandidateView(LoginRequiredMixin, FormView):
    template_name = 'become_candidate.html'
    form_class = CandidateApplicationForm
    success_url = '/'

    def form_valid(self, form):
        application = form.save(user=self.request.user, commit=False)
        application.save()

        # Change user's is_active to False
        self.request.user.is_active = False
        self.request.user.save()

        # Log out the user
        logout(self.request)

        messages.success(self.request, 'Your application to become a candidate has been submitted successfully.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
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

                voter_group = Group.objects.get(name='voter')
                user.groups.remove(voter_group)

                candidate_group = Group.objects.get(name='candidate')
                user.groups.add(candidate_group)

                user.is_active = True
                user.save()
                
                candidate, created = Candidate.objects.get_or_create(
                user=user,
                party=application.party,
                is_approved=True 
                )

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

@method_decorator(login_required, name='dispatch')
class VoteView(LoginRequiredMixin, FormView):
    template_name = 'vote.html'
    form_class = VoteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            polling_schedule = PollingSchedule.objects.latest('start_datetime')
            context['voting_open'] = polling_schedule.is_voting_open()
            context['polling_schedule'] = polling_schedule
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

        if Vote.objects.filter(voter=voter, halka=halka).exists():
            return redirect('vote-cast-multiple-times')
            
        vote = Vote(voter=voter, candidate=candidate, halka=halka)
        vote.save()

        candidate_vote = Vote.objects.get(voter=voter, candidate=candidate)
        candidate_vote.vote_count += 1
        candidate_vote.save()

        messages.success(self.request, 'Your vote has been cast successfully.')
        return redirect('vote-cast-success')

@method_decorator(login_required, name='dispatch')
class VoteCastedSuccessView(TemplateView):
    template_name = 'vote_casted_success.html'

@method_decorator(login_required, name='dispatch')
class VoteCastedMultipleTimesView(TemplateView):
    template_name = 'vote_casted_multiple.html'


@method_decorator(login_required, name='dispatch')
class PollingScheduleView(UserPassesTestMixin, FormView):
    template_name = 'set_polling_schedule.html'
    form_class = PollingScheduleForm

    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Polling schedule has been set successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('superuser-dashboard')

@method_decorator(login_required, name='dispatch')
class CandidateTotalVotesView(LoginRequiredMixin, View):
    template_name = 'candidate_total_votes.html'

    def get(self, request):
        candidate = self.request.user
        candidate_votes = Vote.objects.filter(candidate=candidate)
        total_votes = sum(vote.vote_count for vote in candidate_votes)
        
        try:
            polling_schedule = PollingSchedule.objects.latest('start_datetime')
            now = datetime.now(pytz.timezone('Asia/Karachi'))

            start_date = polling_schedule.start_datetime.date()
            end_date = polling_schedule.end_datetime.date()
            start_time = polling_schedule.start_datetime.time()
            end_time = polling_schedule.end_datetime.time()

            current_date = now.date()
            current_time = now.time()

            if start_date <= current_date <= end_date or current_date >= end_date:
                if current_time > end_time:
                    message = 'Polling has ended. Here are your total votes:'
                elif current_time >= start_time or start_time <= current_time <= end_time:
                    message = 'Polling is in progress. You can view the results later.'
                else:
                    message = 'Polling hasn\'t started yet.'
            else:
                message = 'Polling hasn\'t started yet.'
        except PollingSchedule.DoesNotExist:
            message = 'Polling schedule information not available.'

        context = {
            'candidate': candidate,
            'candidate_votes': candidate_votes,
            'total_votes': total_votes,
            'message': message,
        }
        messages.info(request, message)
        return render(request, self.template_name, context)

@method_decorator(login_required(login_url='login'), name='dispatch')
def candidate_profiles(request):
    candidates = Candidate.objects.filter(is_approved=True)
    return render(request, 'candidate_profiles.html', {'candidates': candidates})

@method_decorator(login_required(login_url='login'), name='dispatch')
class VotersListView(ListView):
    template_name = 'voters_list.html'
    context_object_name = 'voters'

    def get_queryset(self):
        # Retrieve the halka of the logged-in candidate
        candidate_halka = self.request.user.halka

        # Retrieve the voters in the candidate's halka
        voters = CustomUser.objects.filter(halka=candidate_halka, groups__name='voter')
        return voters

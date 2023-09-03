from datetime import datetime
from click import Group
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
import pytz
from FinalProject import settings
from account.decorators import admin_required, candidate_required, voter_required
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
@method_decorator(voter_required, name='dispatch')
class BecomeCandidateView(LoginRequiredMixin, FormView):
    template_name = 'become_candidate.html'
    form_class = CandidateApplicationForm
    success_url = reverse_lazy('become-candidate')

    def form_valid(self, form):
        party_name = form.cleaned_data.get('party_name')
        party_symbol = form.cleaned_data.get('symbol')

        if Party.objects.filter(name=party_name).exists():
            messages.error(self.request, 'A party with this name already exists.')
            return self.form_invalid(form)
    
        if CandidateApplication.objects.filter(user=self.request.user).exists():
            messages.error(self.request, 'You have already submitted an application.')
            return self.form_invalid(form)

        party = Party.objects.create(name=party_name, symbol=party_symbol)

        application = form.save(commit=False)
        application.user = self.request.user
        application.party = party
        application.save()

        messages.success(self.request, 'Your application to become a candidate has been submitted successfully.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
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
                user_halka = user.halka
                candidate_group = Group.objects.get(name='candidate')
                user.groups.add(candidate_group)

                user.is_active = True
                user.save()
                
                candidate, created = Candidate.objects.get_or_create(
                user=user,
                party=application.party,
                halka = user_halka,
                is_approved=True
                )

                send_mail(
                    subject=_('Candidacy Application Approved'),
                    message=_('Congratulations! Your candidacy application has been approved.'),
                    from_email=settings.EMAIL_HOST_USER,  # Use your sender email here
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                
                voter_group = Group.objects.get(name='voter')
                user.groups.remove(voter_group)
                application.delete()

                messages.success(request, 'Application accepted and user promoted to candidate.')
            except CandidateApplication.DoesNotExist:
                messages.error(request, 'Error while accepting application.')

        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
@method_decorator(voter_required, name='dispatch')
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

        try:
            polling_schedule = PollingSchedule.objects.latest('start_datetime')
        except PollingSchedule.DoesNotExist:
            return redirect('no-polling-schedule')

        if Vote.objects.filter(voter=voter, halka=halka, polling_schedule=polling_schedule).exists():
            return redirect('vote-cast-multiple-times')
            
        vote = Vote(voter=voter, candidate=candidate, halka=halka, polling_schedule=polling_schedule)
        vote.save()

        candidate_vote, created = Vote.objects.get_or_create(
            voter=voter, candidate=candidate, halka=halka, polling_schedule=polling_schedule
        )
        candidate_vote.vote_count += 1
        candidate_vote.save()

        messages.success(self.request, 'Your vote has been cast successfully.')
        return redirect('vote-cast-success')


@method_decorator(login_required, name='dispatch')
@method_decorator(voter_required, name='dispatch')
class VoteCastedSuccessView(TemplateView):
    template_name = 'vote_casted_success.html'

@method_decorator(login_required, name='dispatch')
@method_decorator(voter_required, name='dispatch')
class VoteCastedMultipleTimesView(TemplateView):
    template_name = 'vote_casted_multiple.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class PollingScheduleView(UserPassesTestMixin, FormView):
    template_name = 'set_polling_schedule.html'
    form_class = PollingScheduleForm

    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()

    def form_valid(self, form):
        start_datetime = form.cleaned_data['start_datetime']
        end_datetime = form.cleaned_data['end_datetime']
        
        start_date = start_datetime.date()
        end_date = end_datetime.date()
        start_time = start_datetime.time()
        end_time = end_datetime.time()

        now = datetime.now(pytz.timezone('Asia/Karachi'))
        current_date = now.date()
        current_time = now.time()
        
        if start_date < current_date and start_time < current_time:
            messages.error(self.request, 'Start datetime cannot be in the past.')
            return self.form_invalid(form)

        if end_date < current_date and end_time < current_time:
            messages.error(self.request, 'End datetime cannot be in the past.')
            return self.form_invalid(form)

        if start_datetime >= end_datetime:
            messages.error(self.request, 'End datetime should be more than start datetime.')
            return self.form_invalid(form)

        form.save()
        messages.success(self.request, 'Polling schedule has been set successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('set-polling-schedule')


@method_decorator(login_required, name='dispatch')
@method_decorator(candidate_required, name='dispatch')
class CandidateTotalVotesView(LoginRequiredMixin, View):
    template_name = 'candidate_total_votes.html'

    def get(self, request):
        candidate = self.request.user
        
        try:
            # Get the latest polling schedule
            polling_schedule = PollingSchedule.objects.latest('start_datetime')

            # Filter votes by candidate and polling schedule
            candidate_votes = Vote.objects.filter(candidate=candidate, polling_schedule=polling_schedule)

            # Calculate total votes for the candidate
            total_votes = sum(vote.vote_count for vote in candidate_votes)

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
@method_decorator(voter_required, name='dispatch')
class CandidateProfilesView(ListView):
    model = Candidate
    template_name = 'candidate_profiles.html'  # Create a template for rendering candidate profiles
    context_object_name = 'candidates'  # The variable name to use in the template for the list of candidates

    def get_queryset(self):
        # Filter candidates based on the "halka" of the request user
        return Candidate.objects.filter(halka=self.request.user.halka)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You can add additional context data here if needed
        return context



@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(candidate_required, name='dispatch')
class VotersListView(View):
    template_name = 'voters_list.html'

    def get(self, request, *args, **kwargs):
        # Check if the user belongs to a Halka
        if not request.user.halka:
            return HttpResponseForbidden("You don't belong to any Halka")

        # Get the Halka of the current user
        user_halka = request.user.halka

        # Fetch all users with the group 'voter' in the same Halka
        voters_in_same_halka = CustomUser.objects.filter(halka=user_halka, groups__name='voter')

        context = {
            'voters_in_same_halka': voters_in_same_halka,
        }

        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class PreviousPollingScheduleListView(ListView):
    model = PollingSchedule
    template_name = 'previous_polling_schedules.html'
    context_object_name = 'previous_polling_schedules'

    def get_queryset(self):
        # Get all polling schedules
        all_polling_schedules = PollingSchedule.objects.all()

        # Get the current datetime in the 'Asia/Karachi' timezone
        now = datetime.now(pytz.timezone('Asia/Karachi'))

        # Filter polling schedules where the end_datetime is in the past
        # and is_voting_open is False using a list comprehension
        filtered_polling_schedules = [schedule for schedule in all_polling_schedules if not schedule.is_voting_open()]

        return filtered_polling_schedules


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class CandidateListView(ListView):
    model = Candidate
    template_name = 'all_candidates.html'  # Create this template in your app's templates folder
    context_object_name = 'candidates'  # The name to use in the template for the candidate queryset

    def get_queryset(self):
        # You can customize the queryset here, for example, to select related fields
        return Candidate.objects.select_related('user', 'party', 'halka').all()

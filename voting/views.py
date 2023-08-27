from click import Group
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from FinalProject import settings
from account.models import CustomUser
from voting.models import CandidateApplication, PollingSchedule, Vote
from .forms import CandidateApplicationForm
from django.views.generic import ListView
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
from .forms import PollingScheduleForm
from django.contrib.auth.decorators import user_passes_test



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

class VoteView(LoginRequiredMixin, View):
    template_name = 'vote.html'

    def get(self, request):
        polling_schedule = PollingSchedule.objects.first()
        is_polling_active = polling_schedule.is_polling_active()

        voter = request.user
        voter_halka = voter.halka

        # Get candidates from the same halka who are approved
        candidates = CustomUser.objects.filter(groups__name='candidate', halka=voter_halka, is_approved=True)

        return render(request, self.template_name, {'candidates': candidates, 'is_polling_active': is_polling_active})


    def post(self, request):
        selected_candidate_id = request.POST.get('selected_candidate')
        if selected_candidate_id:
            selected_candidate = CustomUser.objects.get(pk=selected_candidate_id)

            # Check if the voter has already voted for this halka
            if Vote.objects.filter(voter=request.user, halka=selected_candidate.halka).exists():
                messages.error(request, 'You have already voted for this halka.')
            else:
                Vote.objects.create(voter=request.user, candidate=selected_candidate, halka=selected_candidate.halka)
                messages.success(request, 'Vote cast successfully.')
        else:
            messages.error(request, 'No candidate selected.')

        return redirect(reverse('voter-dashboard'))  # Replace with appropriate URL

class CandidateResultsView(LoginRequiredMixin, View):
    template_name = 'candidate_results.html'

    def get(self, request):
        if request.user.groups.filter(name='candidate').exists():
            received_votes = Vote.objects.filter(candidate=request.user)
            return render(request, self.template_name, {'received_votes': received_votes})
        else:
            messages.error(request, 'You are not a candidate.')
            return redirect(reverse('voter-dashboard'))  # Replace with appropriate URL


class SetPollingScheduleView(LoginRequiredMixin, View):
    template_name = 'set_polling_schedule.html'
    form_class = PollingScheduleForm

    @user_passes_test(lambda u: u.groups.filter(name='admin').exists(), login_url='voter-dashboard')
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    @user_passes_test(lambda u: u.groups.filter(name='admin').exists(), login_url='voter-dashboard')
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Polling schedule updated successfully.')
            return redirect('voter-dashboard')  # Replace with appropriate URL
        return render(request, self.template_name, {'form': form})

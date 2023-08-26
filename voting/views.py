from click import Group
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from FinalProject import settings
from voting.models import CandidateApplication
from .forms import CandidateApplicationForm
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.contrib.auth import logout


# class CandidateApplicationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
#     template_name = 'candidate_application_list.html'
#     model = CandidateApplication
#     context_object_name = 'applications'

#     def test_func(self):
#         return self.request.user.groups.filter(name='admin').exists()

# class CandidateApplicationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = CandidateApplication
#     fields = ['is_approved']
#     template_name = 'candidate_application_update.html'
#     success_url = reverse_lazy('candidate-application-list')

#     def test_func(self):
#         return self.request.user.groups.filter(name='admin').exists()

#     def form_valid(self, form):
#         instance = form.save()
#         if instance.is_approved:
#             user = instance.user
#             user.is_active = True
#             user.groups.add(Group.objects.get(name='candidate'))
#             user.save()

#             # Send email to the user
#             send_mail(
#                 subject=_('Candidacy Application Approved'),
#                 message=_('Congratulations! Your candidacy application has been approved.'),
#                 from_email=settings.EMAIL_HOST_USER,  # Use your sender email here
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )

#         messages.success(self.request, 'Application status updated.')
#         return super().form_valid(form)

# class BecomeCandidateView(LoginRequiredMixin, FormView):
#     template_name = 'become_candidate.html'
#     form_class = CandidateApplicationForm
#     success_url = '/'  # Change this to the appropriate URL

#     def form_valid(self, form):
#         application = form.save(user=self.request.user, commit=False)
#         application.save()

#         # Change user's is_active to False
#         self.request.user.is_active = False
#         self.request.user.save()

#         # Log out the user
#         logout(self.request)

#         return super().form_valid(form)


# views.py

from click import Group
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from FinalProject import settings
from voting.models import CandidateApplication
from .forms import CandidateApplicationForm
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.contrib.auth import logout
from django.contrib.auth.models import Group  # Import the Group model


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

                # Change user's group to 'candidate'
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

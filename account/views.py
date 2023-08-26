from base64 import urlsafe_b64encode
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, View
from django.http import HttpResponse
from FinalProject import settings
from account.models import CustomUser
from .forms import HalkaForm, LoginForm, SignUpForm
from django.utils.encoding import force_bytes
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .utils import account_activation_token
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic import CreateView, ListView, DeleteView
from .models import Halka
from .forms import HalkaForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import FormView


class ApproveUserView(View):
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_approved = True
        user.save()

        # Generate the activation URL
        user_pk = user.pk
        encoded_pk = urlsafe_base64_encode(force_bytes(user_pk))
        uidb64 = encoded_pk
        token = user.registration_token
        activate_url = reverse('activate-user', args=[uidb64, token])

        # Send the user an email notifying account approval
        mail_subject = 'Your Account has been Approved'
        message = (
            f"Hello {user.username},\n\n"
            f"Your account has been approved by the admin. "
            f"You can now activate your account by clicking the following link:\n\n"
            f"{request.build_absolute_uri(activate_url)}\n\nThank you!"
        )
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()
        return HttpResponse(f'You have approved the user. {user.username} can now activate their account.')

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.registration_token = account_activation_token.make_token(user)
        user.save()

        try:
            self.send_admin_approval_email(user, self.request)
            messages.success(self.request, 'Account created successfully. Please wait for admin approval.')
        except Exception as e:
            messages.error(self.request, 'An error occurred. Please try again later.')

        return super().form_valid(form)
    
    def send_admin_approval_email(self, user, request):
        current_site = get_current_site(request)
        approval_link = request.build_absolute_uri(reverse('approve-user', args=[user.pk]))
        mail_subject = 'New User Registration Approval'
        message = render_to_string('admin_approval_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_b64encode(force_bytes(user.pk)).decode(),
            'token': user.registration_token,
            'approval_link': approval_link,
        })
        admin_email = settings.EMAIL_HOST_USER
        email = EmailMessage(mail_subject, message, to=[admin_email])
        email.send()

class ActivateUserView(View):
    def get(self, request, uidb64, token):
        try:
            # Decode uidb64 to get the primary key value
            user_pk = urlsafe_base64_decode(uidb64)
            user = CustomUser.objects.get(pk=user_pk)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and token == user.registration_token:
            user.is_active = True
            user.save()
            return redirect('login')  # Redirect to the login page after activation
        else:
            return HttpResponse('Activation failed.')

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login failed. Please check your credentials.')
        return super().form_invalid(form)

    def get_success_url(self):
        if self.request.user.groups.filter(name='admin').exists():
            return reverse('superuser-dashboard')  # Redirect to superuser dashboard
        else:
            return reverse('voter-dashboard')  # Redirect to voter dashboard

class SuperuserDashboardView(TemplateView):
    template_name = 'superuser_dashboard.html'

class VoterDashboardView(TemplateView):
    template_name = 'voter_dashboard.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')  


class HalkaAdditionView(UserPassesTestMixin, ListView, FormView):
    template_name = 'halka_addition.html'
    model = Halka
    form_class = HalkaForm  # Include your HalkaForm here
    success_url = reverse_lazy('halka-addition')
    context_object_name = 'halkas'
    extra_context = {'form': form_class()}  # Initialize an instance of the form

    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        form.save()  # This will save the form data to the database
        return super().form_valid(form)

class HalkaDeleteView(UserPassesTestMixin, DeleteView):
    model = Halka
    success_url = reverse_lazy('halka-addition')
    template_name = 'halka_confirm_delete.html'  # Specify the template name here

    def test_func(self):
        return self.request.user.is_superuser

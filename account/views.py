from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import CreateView, View
from django.contrib.auth.views import LoginView
from .forms import LoginForm, SignUpForm
from .models import CustomUser
from django.contrib import messages
from .utils import EmailVerificationSender

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        print('Form is valid.')
        user = form.save(commit=False)
        user.is_active = False
        user.registration_token = user.generate_registration_token()
        user.save()

        # Assign the 'voter' group
        voter_group = Group.objects.get(name='voter')
        user.groups.add(voter_group)

        # Send verification email using EmailVerificationSender class
        EmailVerificationSender.send_verification_email(user.username, user.cnic, user.registration_token)
        print('Email sent successfully.')
        messages.success(self.request, 'Account created successfully. Please check your email for account verification.')
        return super().form_valid(form)


class UserEmailConfirmationView(View):
    def get(self, request, token):
        try:
            user = CustomUser.objects.get(registration_token=token)
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('home')
        except CustomUser.DoesNotExist:
            return redirect('login')

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login failed. Please check your credentials.')
        return super().form_invalid(form)

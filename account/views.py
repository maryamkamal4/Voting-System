from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm, LoginForm

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')  # Redirect to login page after successful signup

    def form_valid(self, form):
        response = super().form_valid(form)
        # Here you can save the user with is_activated=False
        user = form.save(commit=False)
        user.is_activated = False
        user.save()
        messages.success(self.request, 'Account created successfully. Please log in.')
        return response

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login failed. Please check your credentials.')
        return super().form_invalid(form)

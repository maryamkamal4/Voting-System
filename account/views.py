from base64 import urlsafe_b64encode
from django.urls import reverse_lazy
from django.views.generic import CreateView, View
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from FinalProject import settings
from account.models import CustomUser
from .forms import LoginForm, SignUpForm
from django.utils.encoding import force_bytes, force_text
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .utils import account_activation_token
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect


class AdminApprovalView(View):
    template_name = 'admin_approval.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        unapproved_users = CustomUser.objects.filter(is_approved=False)
        return render(request, self.template_name, {'unapproved_users': unapproved_users})

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        user.is_approved = True
        user.save()

        # Send approval email to user
        mail_subject = 'Account Approved'
        message = 'Your account has been approved by the admin. You can now log in.'
        to_email = user.email
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

        return redirect('admin-approval')  # Redirect back to the approval page


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.registration_token = account_activation_token.make_token(user)
        print('token generated')
        user.save()

        # Send email to admin for approval
        current_site = get_current_site(self.request)
        mail_subject = 'New User Registration Approval'
        message = render_to_string('admin_approval_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_b64encode(force_bytes(user.pk)).decode,
            'token': user.registration_token,
        })
        admin_email = settings.EMAIL_HOST_USER
        email = EmailMessage(mail_subject, message, to=[admin_email])
        email.send()
        print('Email sent')
        
        messages.success(self.request, 'Account created successfully. Please wait for admin approval.')
        return super().form_valid(form)


class UserEmailConfirmationView(View):

    def get(self, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_approved = True
            user.is_active = True  # Set the user active after admin approval
            user.save()
            print('User can now login')
            
            # Send approval email to user
            mail_subject = 'Account Approved'
            message = 'Your account has been approved by the admin. You can now log in.'
            to_email = user.email
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            return HttpResponse('Thank you for your email confirmation. Your account has been approved.')
        else:
            return HttpResponse('Activation link is invalid.')


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login failed. Please check your credentials.')
        return super().form_invalid(form)

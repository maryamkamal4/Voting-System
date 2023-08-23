from base64 import urlsafe_b64encode
from django.dispatch import receiver
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, View
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
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.views import LoginView
import logging
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import get_user_model
import pdb


logger = logging.getLogger(__name__)

# class ApproveUserView(View):
#     def get(self, request, pk):
#         user = get_object_or_404(CustomUser, pk=pk)
#         user.is_approved = True
#         user.save()

#         # Send the user an email notifying account approval
#         mail_subject = 'Your Account has been Approved'
#         message = f"Hello {user.username},\n\nYour account has been approved by the admin. You can now log in.\n\nThank you!"
#         email = EmailMessage(mail_subject, message, to=[user.email])
#         email.send()

#         return HttpResponse(f'You have approved the user. {user.username} can now login.')
    
class ApproveUserView(View):
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_approved = True
        user.save()
        # pdb.set_trace()
        # Generate the activation URL
        user_pk = user.pk
        encoded_pk = urlsafe_base64_encode(force_bytes(user_pk))

        # To decode the encoded primary key back to bytes
        uidb64 = urlsafe_base64_decode(encoded_pk)
        # uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = user.registration_token
        activate_url = reverse('activate-user', args=[uidb64, token])
        # Send the user an email notifying account approval
        mail_subject = 'Your Account has been Approved'
        message = f"Hello {user.username},\n\nYour account has been approved by the admin. You can now activate your account by clicking the following link:\n\n{request.build_absolute_uri(activate_url)}\n\nThank you!"
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()
        return HttpResponse(f'You have approved the user. {user.username} can now activate their account.')


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        logger.info("Processing form_valid method in SignUpView")
        user = form.save(commit=False)
        user.is_active = False
        user.registration_token = account_activation_token.make_token(user)
        pdb.set_trace()
        user.save()

        try:
            self.send_admin_approval_email(user, self.request)
            messages.success(self.request, 'Account created successfully. Please wait for admin approval.')
        except Exception as e:
            logger.error(f"Error sending admin approval email: {e}")
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
            'approval_link': approval_link,  # Include the approval link in the context
        })
        admin_email = settings.EMAIL_HOST_USER
        email = EmailMessage(mail_subject, message, to=[admin_email])
        email.send()


class ActivateUserView(View):
    def get(self, request, uidb64, token):
        
        uid_bytes = urlsafe_base64_decode(uidb64)
        uid = int.from_bytes(uid_bytes, byteorder='big')  # Convert bytes to an integer
        pdb.set_trace()
        try:    
            user = CustomUser.objects.get(pk=uid)
            pdb.set_trace()
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and token == user.registration_token:
            user.is_active = True
            user.save()
            return redirect('login')  # Redirect to the login page after activation
        else:
            # Handle invalid activation link, e.g., show an error page
            return HttpResponse(f'Activation failed.')
            
            
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login failed. Please check your credentials.')
        return super().form_invalid(form)

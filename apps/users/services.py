from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import User
from .serializers import UserRegistrationSerializer, UserUpdateSerializer
import random
import string

class UserService:
    @staticmethod
    def create_user(data):
        with transaction.atomic():
            # Generate verification code
            code = ''.join(random.choices(string.digits, k=6))
            data['verification_code'] = code
            
            serializer = UserRegistrationSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Send verification email
            UserService.send_verification_email(user, code)
            
            return user
    
    @staticmethod
    def send_verification_email(user, code):
        subject = 'Verifica tu email - Busca Me'
        html_message = render_to_string('emails/verification.html', {
            'user': user,
            'code': code
        })
        plain_message = strip_tags(html_message)
        send_mail(subject, plain_message, None, [user.email], html_message=html_message)
    
    @staticmethod
    def update_user(user_id, data):
        with transaction.atomic():
            user = User.objects.get(id=user_id)
            serializer = UserUpdateSerializer(user, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            return serializer.save()
    
    @staticmethod
    def verify_user(user_id, code):
        with transaction.atomic():
            user = User.objects.get(id=user_id)
            if user.verification_code == code:
                user.is_verified = True
                user.email_verified = True
                user.verification_code = None
                user.save()
                return user
        return None

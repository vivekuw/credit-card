from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
import string
# Register your models here.
admin.site.site_header = "Shield Trust Bank"
admin.site.site_title = "Credit Card System"
admin.site.index_title = "Credit Card System - Shield Trust Bank"

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')  # Display in admin panel

    def save_model(self, request, obj, form, change):
        if not change:  # Only send email when a new user is created
            password = generate_password()
            obj.set_password(password)  # Hash and save the password
            obj.save()

            # Email details
            subject = "Credit Card System - Login Credentials"
            message = f"""
            Hello {obj.username},

            Your account has been successfully created in the **Credit Card Fraud Detection System**.

            🔹 **Username**: {obj.username}  
            🔹 **Password**: {password}  

            You can login using the following link:  
            🔗 http://sheildtrustcreditcard.com/login/

            Best regards,  
            Shield Trust Bank
            """

            send_mail(subject, message, 'noreply@sheildtrustbank.com', [obj.email])

        super().save_model(request, obj, form, change)


# Unregister default User admin and register custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

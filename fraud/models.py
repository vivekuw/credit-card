from django.db import models
from django.utils.timezone import now
import pytz

def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return now().astimezone(ist)
# Create your models here.
class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    date_of_birth = models.DateField()
    created_at = models.DateTimeField()

class Card(models.Model):
    card_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='Cards')
    card_number = models.CharField(max_length=20, unique=True)
    expiry_date = models.DateField()
    cvv = models.IntegerField()
    card_type = models.CharField(max_length=20)
    credit_limit = models.IntegerField()
    balance = models.IntegerField()
    is_active = models.CharField(max_length=3)

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    card = models.ForeignKey('Card', on_delete=models.CASCADE,related_name='transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    merchant_name = models.CharField(max_length=255)
    merchant_category = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

class FraudAlerts(models.Model):
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name='fraud')
    anomaly_score = models.FloatField()
    threshold = models.FloatField()
    created_at = models.DateField(auto_now_add=True)
    alert_sent = models.BooleanField(default=False)
    sent_timestamp = models.DateField(null=True, blank=True)

class IsFraud(models.Model):
    id = models.AutoField(primary_key=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    is_fraud = models.IntegerField(default=0)

class FraudAlertEmails(models.Model):
    email_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fraud_emails')
    alert = models.ForeignKey('FraudAlerts', on_delete=models.CASCADE, related_name='email_alerts')
    email_subject = models.CharField(max_length=255)
    email_body = models.TextField()
    sent_at = models.DateField(auto_now_add=True)
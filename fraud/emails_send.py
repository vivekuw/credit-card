from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now
from .models import *

def send_fraud_alerts_emails():
    fraud_alerts = FraudAlerts.objects.filter(alert_sent=False)
    for alert in fraud_alerts:
        transaction = alert.transaction
        card = transaction.card
        user = card.user
        subject = "Shield Trust Bank - Fraud Alert: Suspicious Transaction Detected!"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 600px; background: #ffffff; padding: 20px; border-radius: 8px;
                              box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); text-align: left; }}
                .header {{ background-color: #d32f2f; color: white; padding: 10px; text-align: center;
                           font-size: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 20px; color: #333; }}
                .highlight {{ font-weight: bold; color: #d32f2f; }}
                .button {{ display: inline-block; background: #d32f2f; color: white; padding: 12px 20px;
                           text-decoration: none; border-radius: 5px; font-size: 16px; margin-top: 15px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #777; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">⚠ Suspicious Transaction Alert</div>
                <div class="content">
                    <p>Dear <strong>{user.name}</strong>,</p>
                    <p>We have detected a <span class="highlight">suspicious transaction</span> on your <strong>Shield Trust Bank</strong> account.</p>
                    <h3>Transaction Details:</h3>
                    <ul>
                        <li><strong>Amount:</strong> {transaction.amount}</li>
                        <li><strong>Merchant:</strong> {transaction.merchant_name}</li>
                        <li><strong>Location:</strong> {transaction.location}</li>
                        <li><strong>Date:</strong> {transaction.date}</li>
                    </ul>
                    <p>If you recognize this transaction, no action is needed.</p>
                    <p>If <span class="highlight">this was not you</span>, please <strong>report it immediately</strong>:</p>
                    
                    <p class="footer">Shield Trust Bank prioritizes your security.</p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body="This is an HTML email. Please view it in an email client that supports HTML.",
                from_email="noreply@shieldtrustbank.com",
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            # Log the email
            FraudAlertEmails.objects.create(
                user=user,
                alert=alert,
                email_subject=subject,
                email_body=html_content,
                sent_at=now()
            )
            alert.alert_sent = True
            alert.sent_timestamp = now()
            alert.save(update_fields=['alert_sent', 'sent_timestamp'])

            print(f"Email sent - {alert.id}")

        except Exception as e:
            print(f"Failed - {alert.id}: {e}")

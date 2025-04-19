from django.db.models import F
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .models import *
from .ml_model import *
# Create your views here.

def signout(request):
    logout(request)
    return redirect('/')

@login_required
def home(request):
    total_transaction = Transaction.objects.count()
    total_fraud = FraudAlerts.objects.count()
    active_cards = Card.objects.filter(is_active="yes").count()
    block_card = Card.objects.filter(is_active="no").count()
    context = {
        "block_card": block_card,
        "total_transactions": total_transaction,
        "active_cards": active_cards,
        "fraud_cases": total_fraud,
    }
    return render(request, 'home.html', context)


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/home')
        else:
            msg = 'Error Login'
            form = AuthenticationForm(request.POST)
            return render(request, 'login.html', {'form': form, 'msg': msg})
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

@login_required
def transactions(request):
    transactions = Transaction.objects.all()
    isfraud = IsFraud.objects.all()
    return render(request,'transaction.html',{'transactions':transactions,'isfraud':isfraud})

@login_required
def fraud_view(request):
    fraud_alerts = FraudAlerts.objects.all()
    return render(request, 'fraud.html', {'fraud_alerts': fraud_alerts})

@login_required()
def dashboard(request):
    return render(request,'dashboard.html')

@login_required()
def get_chart_data(request, chart_type):
    if chart_type == "fraudulent_transactions":
        fraud_data = IsFraud.objects.values('is_fraud').annotate(count=Count('is_fraud'))

        labels = ["Not Fraud", "Fraud"]
        values = [
            next((entry['count'] for entry in fraud_data if entry['is_fraud'] == 0), 0),
            next((entry['count'] for entry in fraud_data if entry['is_fraud'] == 1), 0)
        ]

        chart_data = {
            "title": "Fraudulent Transactions",
            "labels": labels,
            "values": values,
            "colors": ["#36A2EB", "#FF6384"],
            "chartType": "pie"
        }

    elif chart_type == "card_status":
        status_data = Card.objects.values('is_active').annotate(count=Count('is_active'))
        labels = ["Inactive", "Active"]
        values = [
            next((entry['count'] for entry in status_data if entry['is_active'] == "no"), 0),
            next((entry['count'] for entry in status_data if entry['is_active'] == 'yes'), 0)
        ]

        chart_data = {
            "title": "Card Status Distribution",
            "labels": labels,
            "values": values,
            "colors": ["#FFA500", "#008000"],
            "chartType": "pie"
        }

    elif chart_type == "transactions_overview":
        transactions = Transaction.objects.values('date').annotate(total_amount=Sum('amount')).order_by('date')
        labels = [entry['date'].strftime('%Y-%m-%d') for entry in transactions]
        values = [entry['total_amount'] for entry in transactions]
        chart_data = {
            "title": "Transactions Overview",
            "labels": labels,
            "values": values,
            "colors": "#36A2EB",
            "chartType": "line"
        }


    elif chart_type == "credit_utilization":

        users = (
            Card.objects.values('user_id')
            .annotate(credit_utilized=Sum(F('credit_limit') - F('balance')))
            .order_by('-credit_utilized')[:30]  # Get top 30 users
        )
        labels = [str(entry['user_id']) for entry in users]
        values = [entry['credit_utilized'] for entry in users]
        chart_data = {
            "title": "Top 30 Users - Credit Utilization",
            "labels": labels,
            "values": values,
            "colors": ["#8A2BE2", "#5F9EA0", "#FF4500"],
            "chartType": "bar"

        }


    elif chart_type == "merchant_transactions":
        merchants = Transaction.objects.values('merchant_category').annotate(total_amount=Sum('amount'))
        labels = [entry['merchant_category'] for entry in merchants]
        values = [entry['total_amount'] for entry in merchants]
        chart_data = {
            "title": "Merchant Category-wise Transactions",
            "labels": labels,
            "values": values,
            "colors": ["#4BC0C0", "#FF6384", "#36A2EB", "#FFCE56"],
            "chartType": "bar"
        }


    elif chart_type == "fraud_by_location":
        fraud_locations = (
            IsFraud.objects.filter(is_fraud=1)  # Get only fraud transactions
            .values(location=F('transaction__location'))  # Fetch location from Transaction table
            .annotate(count=Count('id'))  # Count fraud cases
            .order_by('-count')  # Optional: Sort by highest fraud cases
        )

        labels = [entry['location'] for entry in fraud_locations]
        values = [entry['count'] for entry in fraud_locations]
        chart_data = {
            "title": "Fraud Transactions by Location",
            "labels": labels,
            "values": values,
            "colors": [
                "#FF4500", "#5F9EA0", "#36A2EB", "#FFD700", "#8A2BE2",
                "#FF69B4", "#20B2AA", "#DC143C", "#32CD32", "#8B0000",
                "#FF8C00", "#4B0082"
            ],
            "chartType": "pie"
        }

    elif chart_type == "fraud_anomaly_scores":
        anomalies = FraudAlerts.objects.values('transaction_id', 'anomaly_score')
        labels = [str(entry['transaction_id']) for entry in anomalies]
        values = [entry['anomaly_score'] for entry in anomalies]
        chart_data = {
            "title": "Fraud Anomaly Scores",
            "labels": labels,
            "values": values,
            "colors": "#FF4500",
            "chartType": "scatter"
        }
    else:
        return JsonResponse({"error": "Invalid chart type"}, status=400)

    return JsonResponse(chart_data)

@login_required()
def cards(request):
    cards = Card.objects.all()
    return render(request,'card.html',{'cards':cards})

@login_required()
def upload_csv(request):
    if request.method =="POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith("csv"):
            messages.error(request,"please")
            return redirect("upload_csv")
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                try:
                    card = Card.objects.get(card_id=row["card_id"])
                    transaction = Transaction.objects.create(
                        card=card,
                        amount=row["amount"],
                        merchant_name=row["merchant_name"],
                        merchant_category=row["merchant_category"],  # Added category
                        date=row["date"],
                        location=row["location"],
                        status=row["status"],
                    )
                    transaction.save()
                except Exception as e:
                    messages.error(request, f"Error processing row {row.to_dict()}: {e}")
            messages.success(request, "CSV uploaded successfully!")
        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
        return redirect("upload_csv")
    return render(request,'upload.html')

def active_cards(request):
    cards = Card.objects.filter(is_active='yes')
    return render(request, 'card.html',{'cards':cards})
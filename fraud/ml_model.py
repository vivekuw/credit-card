import joblib
import pandas as pd
from django.shortcuts import get_object_or_404
from .models import Transaction, FraudAlerts, Card, IsFraud

label_encoders = joblib.load("./fraud/label_encoders.sav")
scaler = joblib.load("./fraud/scaler.sav")
isolation_forest = joblib.load("./fraud/isolation_forest.sav")
logistic_regression = joblib.load("./fraud/logistic_model.sav")

categorical_cols = ["merchant_name", "merchant_category", "location", "status", "card_type", "is_active"]
numerical_cols = ["amount", "credit_limit", "balance"]

def predict_fraud(transaction_id, isolation_threshold=-0.1, logistic_threshold=0.7):
    try:
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
        card = get_object_or_404(Card, card_id=transaction.card.card_id)
        input_data = {
            "merchant_name": transaction.merchant_name,
            "merchant_category": transaction.merchant_category,
            "location": transaction.location,
            "status": transaction.status,
            "card_type": card.card_type,
            "is_active": card.is_active,
            "amount": transaction.amount,
            "credit_limit": card.credit_limit,
            "balance": card.balance,
            "date": transaction.date
        }

        df = pd.DataFrame([input_data])

        for col in categorical_cols:
            if col in label_encoders:
                df[col] = label_encoders[col].transform(df[col])
            else:
                raise ValueError(f"label encoder column '{col}' not found.")

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["day"] = df["date"].dt.day
        df["month"] = df["date"].dt.month
        df["hour"] = df["date"].dt.hour
        df["weekday"] = df["date"].dt.weekday
        df = df.drop(columns=["date"], errors="ignore")

        df[numerical_cols] = scaler.transform(df[numerical_cols])

        anomaly_score = isolation_forest.decision_function(df)[0]
        fraud_probability = logistic_regression.predict_proba(df)[:, 1][0]

        is_fraud = int((anomaly_score < isolation_threshold) or (fraud_probability > logistic_threshold))
        # isolation_threshold=-0.1, logistic_threshold=0.7
        if is_fraud:

            fraud_alert, created = FraudAlerts.objects.update_or_create(
                transaction=transaction,
                defaults={
                    "anomaly_score": anomaly_score,
                    "threshold": fraud_probability,
                    "alert_sent": False,
                    "sent_timestamp": None,
                }
            )
            fraud_alert.card_id = card.card_id
            fraud_alert.save()
            if created:
                print(f"fraud alert created- transaction id {transaction_id}")
            else:
                print(f"fraud alert updated- transaction id {transaction_id}")
        is_fraud_record, created = IsFraud.objects.update_or_create(
            transaction=transaction,
            defaults={"is_fraud": is_fraud}
        )
        if created:
            print(f"transaction id - {transaction_id} recorded in isfraud table.")
        else:
            print(f"transaction id- {transaction_id} updated in isfraud table.")
        return is_fraud_record
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

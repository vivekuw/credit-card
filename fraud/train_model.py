import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, precision_score
from imblearn.over_sampling import SMOTE
import joblib
df = pd.read_csv("merged_transactions_with_cards.csv")

columns_to_drop = ["transaction_id", "card_id", "user_id", "card_number", "cvv", "expiry_date",
                   "name", "email", "phone_number", "address", "date_of_birth", "created_at"]
df = df.drop(columns=columns_to_drop, errors="ignore")

categorical_cols = ["merchant_name", "merchant_category", "location", "status", "card_type", "is_active"]
label_encoders = {col: LabelEncoder() for col in categorical_cols}
for col in categorical_cols:
    df[col] = label_encoders[col].fit_transform(df[col])

df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
df["day"] = df["date"].dt.day
df["month"] = df["date"].dt.month
df["hour"] = df["date"].dt.hour  # New feature: Transaction Hour
df["weekday"] = df["date"].dt.weekday  # New feature: Day of the week
df = df.drop(columns=["date"], errors="ignore")

scaler = StandardScaler()
numerical_cols = ["amount", "credit_limit", "balance"]
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

iso_forest = IsolationForest(n_estimators=1000, contamination=0.05, random_state=42)
df["Fraud_Label"] = iso_forest.fit_predict(df.drop(columns=["Fraud_Label"], errors="ignore"))
df["Fraud_Label"] = df["Fraud_Label"].map({1: 0, -1: 1})  # Convert -1 (anomalies) to 1 (fraud), 1 to 0 (normal)

X = df.drop(columns=["Fraud_Label"])
y = df["Fraud_Label"]

# SMOTE
smote = SMOTE( random_state=42)
X_numeric = X.select_dtypes(include=['number'])
X_resampled, y_resampled = smote.fit_resample(X_numeric, y)

# Split
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled)

# Train model
log_reg = LogisticRegression(max_iter=1000, random_state=42)
log_reg.fit(X_train, y_train)

# Predict
y_pred = log_reg.predict(X_test)

print(iso_forest.feature_names_in_)
# Model evaluation
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)

#results
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Classification Report:\n", classification_rep)

joblib.dump(label_encoders, "label_encoders.sav")
joblib.dump(scaler, "scaler.sav")
joblib.dump(iso_forest, "isolation_forest.sav")
joblib.dump(log_reg, "logistic_model.sav")
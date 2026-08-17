import os
import random

import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report,
)


# -------------------------------------------------
# 1. CREATE A SIMULATED LOGIN BEHAVIOR DATASET
# -------------------------------------------------

random.seed(42)

records = []

for _ in range(1000):

    login_hour = random.randint(0, 23)

    day_of_week = random.randint(0, 6)

    login_frequency = random.randint(1, 10)

    # 1 = Successful authentication
    # 0 = Failed authentication
    login_status = random.randint(0, 1)

    # 0 = Known/normal network
    # 1 = Unknown/unusual network
    ip_risk = random.randint(0, 1)

    # Create behavioral risk score
    risk_score = 0

    # Unusual late-night / early-morning login
    if login_hour < 6 or login_hour > 22:
        risk_score += 2

    # High login frequency
    if login_frequency >= 7:
        risk_score += 2

    # Failed authentication
    if login_status == 0:
        risk_score += 1

    # Unknown/unusual IP
    if ip_risk == 1:
        risk_score += 2

    # Label:
    # 0 = Normal
    # 1 = Suspicious
    suspicious = 1 if risk_score >= 3 else 0

    records.append(
        [
            login_hour,
            day_of_week,
            login_frequency,
            login_status,
            ip_risk,
            suspicious,
        ]
    )


columns = [
    "login_hour",
    "day_of_week",
    "login_frequency",
    "login_status",
    "ip_risk",
    "suspicious",
]


df = pd.DataFrame(records, columns=columns)


# -------------------------------------------------
# 2. SAVE DATASET
# -------------------------------------------------

current_directory = os.path.dirname(os.path.abspath(__file__))

dataset_path = os.path.join(
    current_directory,
    "login_behavior_dataset.csv"
)

df.to_csv(dataset_path, index=False)


# -------------------------------------------------
# 3. PREPARE FEATURES AND TARGET
# -------------------------------------------------

X = df[
    [
        "login_hour",
        "day_of_week",
        "login_frequency",
        "login_status",
        "ip_risk",
    ]
]

y = df["suspicious"]


# -------------------------------------------------
# 4. TRAIN / TEST SPLIT
# -------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


# -------------------------------------------------
# 5. RANDOM FOREST MODEL
# -------------------------------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# -------------------------------------------------
# 6. PREDICTION
# -------------------------------------------------

y_pred = model.predict(X_test)


# -------------------------------------------------
# 7. MODEL EVALUATION
# -------------------------------------------------

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)


print("\n--------------------------------")
print(" RANDOM FOREST MODEL RESULTS")
print("--------------------------------")

print(f"Accuracy  : {accuracy * 100:.2f}%")
print(f"Precision : {precision * 100:.2f}%")
print(f"Recall    : {recall * 100:.2f}%")
print(f"F1 Score  : {f1 * 100:.2f}%")

print("\nClassification Report:\n")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Normal", "Suspicious"],
        zero_division=0
    )
)


# -------------------------------------------------
# 8. CONFUSION MATRIX
# -------------------------------------------------

cm = confusion_matrix(y_test, y_pred)

display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Normal", "Suspicious"]
)

display.plot()

plt.title(
    "Random Forest - Confusion Matrix"
)

plt.tight_layout()

confusion_matrix_path = os.path.join(
    current_directory,
    "confusion_matrix.png"
)

plt.savefig(
    confusion_matrix_path,
    dpi=300
)

plt.close()


# -------------------------------------------------
# 9. FEATURE IMPORTANCE GRAPH
# -------------------------------------------------

feature_names = [
    "Login Hour",
    "Day of Week",
    "Login Frequency",
    "Login Status",
    "IP Risk",
]

importance = model.feature_importances_

plt.figure(figsize=(8, 5))

plt.bar(
    feature_names,
    importance
)

plt.title(
    "Random Forest Feature Importance"
)

plt.ylabel(
    "Importance"
)

plt.xticks(
    rotation=25
)

plt.tight_layout()

feature_graph_path = os.path.join(
    current_directory,
    "feature_importance.png"
)

plt.savefig(
    feature_graph_path,
    dpi=300
)

plt.close()


# -------------------------------------------------
# 10. SAVE TRAINED MODEL
# -------------------------------------------------

model_path = os.path.join(
    current_directory,
    "login_model.pkl"
)

joblib.dump(
    model,
    model_path
)


print("\nFiles created successfully:")

print(dataset_path)

print(model_path)

print(confusion_matrix_path)

print(feature_graph_path)
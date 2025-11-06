import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, matthews_corrcoef
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

print("Starting model training process...")

# --- 1. Load Data ---
try:
    df = pd.read_csv('creditcard.csv')
    print("Dataset loaded successfully.")
except FileNotFoundError:
    print("Error: 'creditcard.csv' not found. Make sure it's in the 'backend' directory.")
    exit()

# --- 2. Preprocess Data ---
# Separate features (X) and target (y)
X = df.drop('Class', axis=1)
y = df['Class']

# Scale the 'Amount' and 'Time' columns
# Using StandardScaler to normalize the data
scaler = StandardScaler()
X['scaled_amount'] = scaler.fit_transform(X['Amount'].values.reshape(-1, 1))
X['scaled_time'] = scaler.fit_transform(X['Time'].values.reshape(-1, 1))
X = X.drop(['Time', 'Amount'], axis=1)
print("Data preprocessing and scaling complete.")

# --- 3. Split Data ---
# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print("Data split into training and testing sets.")

# --- 4. Train Model ---
# Using Logistic Regression, which is good for this type of binary classification
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)
print("Model training complete.")

# --- 5. Evaluate Model & Get Metrics ---
# This is where we get the numbers for our website display
y_pred = model.predict(X_test)

# Calculate the confusion matrix values
# .ravel() flattens the matrix into a simple array [tn, fp, fn, tp]
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

# Calculate performance metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
# New metrics
f1 = f1_score(y_test, y_pred)
mcc = matthews_corrcoef(y_test, y_pred)
specificity = tn / (tn + fp)

metrics = {
    "tn": int(tn), "fp": int(fp),
    "fn": int(fn), "tp": int(tp),
    "accuracy": accuracy,
    "precision": precision,
    "recall": recall,
    "f1_score": f1,
    "specificity": specificity,
    "mcc": mcc
}
print("Model evaluation complete. Metrics:")
print(metrics)

# --- Confusion Matrix Plot ---
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Fraud', 'Fraud'], yticklabels=['Not Fraud', 'Fraud'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.tight_layout()
plt.show()

# --- 6. Save Artifacts ---
# Create the ml_assets directory if it doesn't already exist
output_dir = 'ml_assets'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Use joblib to serialize and save the Python objects to files
joblib.dump(model, os.path.join(output_dir, 'fraud_detection_model.pkl'))
joblib.dump(metrics, os.path.join(output_dir, 'model_metrics.pkl'))
joblib.dump(scaler, os.path.join(output_dir, 'scaler.pkl'))

print(f"\nSuccess! Model, metrics, and scaler have been saved to the '{output_dir}/' directory.")
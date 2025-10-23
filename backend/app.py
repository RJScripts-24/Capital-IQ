from flask import Flask, request, jsonify
from flask_cors import CORS # Import the CORS library
import pandas as pd
import joblib
import os

# Initialize the Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow your React frontend
# to communicate with this backend.
CORS(app)

# --- 1. Load the pre-trained assets ---
# This block of code runs only once when the server starts.
try:
    model_path = os.path.join('ml_assets', 'fraud_detection_model.pkl')
    metrics_path = os.path.join('ml_assets', 'model_metrics.pkl')
    scaler_path = os.path.join('ml_assets', 'scaler.pkl')

    model = joblib.load(model_path)
    metrics_data = joblib.load(metrics_path)
    
    # Convert numpy types to Python native types for JSON serialization
    for key, value in metrics_data.items():
        if hasattr(value, 'item'):  # Check if it's a numpy type with item() method
            metrics_data[key] = value.item()
    
    scaler = joblib.load(scaler_path)
    print("✅ Model, metrics, and scaler loaded successfully.")
except FileNotFoundError as e:
    print(f"❌ Error loading .pkl files: {e}")
    print("Please ensure you have run 'train_model.py' and the files are in the 'ml_assets' directory.")
    # Exit if we can't load the essential files
    exit()

def perform_expenditure_analysis(df):
    """Performs expenditure analysis and generates a savings plan."""
    # This function requires 'Amount' and a 'Category' column in the user's CSV.
    if 'Category' not in df.columns or 'Amount' not in df.columns:
        return {
            "error": "CSV must contain 'Category' and 'Amount' columns for analysis.",
            "total_spend": 0,
            "spend_by_category": {},
            "savings_plan": {}
        }
    
    total_spend = df['Amount'].sum()
    spend_by_category = df.groupby('Category')['Amount'].sum().round(2).to_dict()
    
    # Simple Savings Plan Logic
    savings_plan = {}
    non_essential = ['Dining', 'Entertainment', 'Shopping', 'Travel'] # Example categories
    for category, amount in spend_by_category.items():
        if category in non_essential and amount > 50: # Set a threshold
            potential_savings = amount * 0.15 # Suggest saving 15%
            savings_plan[category] = f"You could save ${potential_savings:.2f}/month by reducing spending on {category} by 15%."

    return {
        "total_spend": round(total_spend, 2),
        "spend_by_category": spend_by_category,
        "savings_plan": savings_plan
    }

# --- 2. Define the API Endpoint ---
# This endpoint will handle the file uploads and return the analysis.
@app.route('/analyze', methods=['POST'])
def analyze_transactions():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        user_df = pd.read_csv(file)

        # --- Part A: Expenditure Analysis on raw data ---
        analysis_results = perform_expenditure_analysis(user_df.copy())
        
        # --- Part B: Anomaly Detection using the trained model ---
        # IMPORTANT: The model requires the user's CSV to have the same structure
        # as the training data ('Time', 'V1'-'V28', 'Amount').
        # We will check for the essential columns.
        required_cols = ['Time', 'Amount'] + [f'V{i}' for i in range(1, 29)]
        if not all(col in user_df.columns for col in required_cols):
             return jsonify({
                 "error": "CSV is missing required columns for anomaly detection.",
                 "details": "The model requires 'Time', 'Amount', and 'V1' through 'V28' columns."
             }), 400

        user_df_processed = user_df.copy()
        user_df_processed['scaled_amount'] = scaler.transform(user_df_processed['Amount'].values.reshape(-1, 1))
        user_df_processed['scaled_time'] = scaler.transform(user_df_processed['Time'].values.reshape(-1, 1))
        user_df_processed = user_df_processed.drop(['Time', 'Amount'], axis=1)

        # Reorder columns to match the model's training data
        model_features = list(model.feature_names_in_)
        user_df_processed = user_df_processed[model_features]

        # Predict anomalies
        predictions = model.predict(user_df_processed)
        user_df['is_anomaly'] = predictions
        
        anomalies = user_df[user_df['is_anomaly'] == 1].to_dict(orient='records')

        # --- Part C: Combine all results into a single response ---
        response_data = {
            "model_performance": metrics_data, # From the loaded .pkl file
            "user_anomalies": anomalies,       # From the user's data
            "expenditure_analysis": analysis_results # Also from the user's data
        }
        
        return jsonify(response_data)

    except Exception as e:
        # Generic error handler for issues like malformed CSVs
        return jsonify({"error": "An error occurred during processing", "details": str(e)}), 500

# --- 3. Run the App ---
if __name__ == '__main__':
    # Runs the Flask server on http://127.0.0.1:5000
    app.run(debug=True)
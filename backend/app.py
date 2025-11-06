import matplotlib
matplotlib.use('Agg')
from flask import Flask, request, jsonify
from flask_cors import CORS # Import the CORS library
import pandas as pd
import joblib
import os
from groq import Groq
from dotenv import load_dotenv
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow your React frontend
# to communicate with this backend.
CORS(app)

# Configure Groq API
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    print("⚠️  Warning: GROQ_API_KEY environment variable not set. AI features will not work.")
    groq_client = None

# --- 1. Load the pre-trained assets ---
# This block of code runs only once when the server starts.
try:
    # Get the directory where app.py is located
    app_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(app_dir, 'ml_assets', 'fraud_detection_model.pkl')
    metrics_path = os.path.join(app_dir, 'ml_assets', 'model_metrics.pkl')
    scaler_path = os.path.join(app_dir, 'ml_assets', 'scaler.pkl')

    fraud_model = joblib.load(model_path)
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
        model_features = list(fraud_model.feature_names_in_)
        user_df_processed = user_df_processed[model_features]

        # Predict anomalies
        predictions = fraud_model.predict(user_df_processed)
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

def parse_natural_language_query(query):
    """Use Groq to parse natural language query and extract data requirements."""
    if not groq_client:
        return {"error": "Groq API not configured"}
    
    prompt = f"""
    Parse this natural language financial query and extract the key data requirements.
    Return ONLY a valid JSON object with the following structure (no markdown, no extra text):
    {{
        "query_type": "spending_comparison" | "total_spending" | "category_spending" | "anomaly_count" | "savings_analysis",
        "category": "string or null" (e.g., "coffee", "dining", "shopping"),
        "time_period": "last_month" | "this_month" | "last_week" | "this_week" | "all_time" | null,
        "comparison": "month_over_month" | "category_comparison" | null
    }}
    
    Query: "{query}"
    
    Examples:
    - "How much did I spend on coffee last month vs this month?" -> {{"query_type": "spending_comparison", "category": "coffee", "time_period": null, "comparison": "month_over_month"}}
    - "What's my total spending?" -> {{"query_type": "total_spending", "category": null, "time_period": null, "comparison": null}}
    - "How much did I spend on dining?" -> {{"query_type": "category_spending", "category": "dining", "time_period": null, "comparison": null}}
    """
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",  # Latest fast and accurate model
            temperature=0.1,
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Parse the JSON response
        import json
        result = json.loads(response_text)
        return result
    except Exception as e:
        return {"error": f"Failed to parse query: {str(e)}"}

def analyze_query_with_data(query_requirements, df):
    """Analyze the data based on parsed query requirements."""
    if 'error' in query_requirements:
        return query_requirements
    
    query_type = query_requirements.get('query_type')
    category = query_requirements.get('category')
    time_period = query_requirements.get('time_period')
    comparison = query_requirements.get('comparison')
    
    # For simplicity, let's assume Time represents days (1-30 for a month)
    # We'll simulate month separation
    current_month_data = df[df['Time'] <= 30]  # First 30 days as current month
    last_month_data = df[(df['Time'] > 30) & (df['Time'] <= 60)]  # Next 30 days as last month
    
    if query_type == 'spending_comparison' and comparison == 'month_over_month' and category:
        # Filter by category (case insensitive partial match)
        current_month_cat = current_month_data[
            current_month_data['Category'].str.contains(category, case=False, na=False)
        ]
        last_month_cat = last_month_data[
            last_month_data['Category'].str.contains(category, case=False, na=False)
        ]
        
        current_spend = current_month_cat['Amount'].sum()
        last_spend = last_month_cat['Amount'].sum()
        
        return {
            "response": f"You spent ${last_spend:.2f} last month and ${current_spend:.2f} this month on {category}.",
            "data": {
                "last_month": round(last_spend, 2),
                "this_month": round(current_spend, 2),
                "category": category
            }
        }
    
    elif query_type == 'total_spending':
        total = df['Amount'].sum()
        return {
            "response": f"Your total spending is ${total:.2f}.",
            "data": {"total_spending": round(total, 2)}
        }
    
    elif query_type == 'category_spending' and category:
        category_data = df[df['Category'].str.contains(category, case=False, na=False)]
        total = category_data['Amount'].sum()
        return {
            "response": f"You spent ${total:.2f} on {category}.",
            "data": {"category_spending": round(total, 2), "category": category}
        }
    
    elif query_type == 'anomaly_count':
        anomalies = df[df['is_anomaly'] == 1] if 'is_anomaly' in df.columns else pd.DataFrame()
        count = len(anomalies)
        return {
            "response": f"You have {count} detected anomalous transactions.",
            "data": {"anomaly_count": count}
        }
    
    else:
        return {"response": "I'm sorry, I couldn't understand that query. Please try asking about spending amounts, categories, or anomalies."}

# --- 4. Natural Language Query Endpoint ---
@app.route('/query', methods=['POST'])
def natural_language_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    query = data['query']
    
    # For now, we'll need the user to upload data first. In a real app, you'd store this in a database.
    # For this demo, we'll check if there's a recent upload or use sample data
    try:
        # Try to load the large_test_data.csv as sample data
        app_dir = os.path.dirname(os.path.abspath(__file__))
        sample_data_path = os.path.join(app_dir, 'large_test_data.csv')
        sample_df = pd.read_csv(sample_data_path)
        sample_df['is_anomaly'] = 0  # Add anomaly column for demo
        
        # Parse the query
        query_requirements = parse_natural_language_query(query)
        
        # Analyze with data
        result = analyze_query_with_data(query_requirements, sample_df)
        
        return jsonify(result)
    
    except FileNotFoundError:
        return jsonify({"error": "No data available. Please upload a CSV file first using the /analyze endpoint."}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred during query processing", "details": str(e)}), 500

def simulate_financial_decision(scenario, df):
    """Simulate the impact of financial decisions."""
    if not groq_client:
        return {"error": "Groq API not configured"}
    
    # Calculate current metrics
    total_spend = df['Amount'].sum()
    spend_by_category = df.groupby('Category')['Amount'].sum().to_dict()
    
    # Assume a 6-month savings plan with 15% monthly savings
    monthly_savings_rate = 0.15
    months = 6
    
    prompt = f"""
    Analyze this financial scenario and provide a realistic simulation.
    Current data:
    - Total spending: ${total_spend:.2f}
    - Monthly spending categories: {spend_by_category}
    - Current savings plan: {monthly_savings_rate*100}% of spending per month for {months} months
    
    Scenario: "{scenario}"
    
    Provide ONLY a valid JSON response (no markdown, no extra text) with:
    {{
        "impact_description": "description of the impact",
        "original_6month_savings": "calculated amount",
        "new_6month_savings": "adjusted amount after scenario",
        "monthly_change": "amount saved/lost per month",
        "recommendations": ["list", "of", "recommendations"]
    }}
    """
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",  # Latest fast and accurate model
            temperature=0.3,
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        import json
        result = json.loads(response_text)
        return result
    except Exception as e:
        return {"error": f"Failed to simulate scenario: {str(e)}"}

# --- 5. What-If Simulation Endpoint ---
@app.route('/simulate', methods=['POST'])
def what_if_simulation():
    data = request.get_json()
    if not data or 'scenario' not in data:
        return jsonify({"error": "No scenario provided"}), 400
    
    scenario = data['scenario']
    
    try:
        # Load sample data
        app_dir = os.path.dirname(os.path.abspath(__file__))
        sample_data_path = os.path.join(app_dir, 'large_test_data.csv')
        sample_df = pd.read_csv(sample_data_path)
        
        # Run simulation
        result = simulate_financial_decision(scenario, sample_df)
        
        return jsonify(result)
    
    except FileNotFoundError:
        return jsonify({"error": "No data available. Please upload a CSV file first."}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred during simulation", "details": str(e)}), 500

# --- 6. Confusion Matrix Endpoint ---
@app.route('/confusion-matrix', methods=['POST'])
def confusion_matrix_api():
    try:
        # Load the latest test data and predictions
        app_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(app_dir, 'ml_assets', 'fraud_detection_model.pkl')
        scaler_path = os.path.join(app_dir, 'ml_assets', 'scaler.pkl')
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)

        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        df = pd.read_csv(file)

        # Check required columns
        required_cols = ['Time', 'Amount'] + [f'V{i}' for i in range(1, 29)]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({'error': f'Missing required columns: {missing_cols}'}), 400

        # Preprocess
        # Save Class column before preprocessing
        y_true = df['Class'].values if 'Class' in df.columns else [0]*len(df)

        df['scaled_amount'] = scaler.transform(df['Amount'].values.reshape(-1, 1))
        df['scaled_time'] = scaler.transform(df['Time'].values.reshape(-1, 1))
        X = df.drop(['Time', 'Amount', 'Category', 'Class'], axis=1, errors='ignore')
        if hasattr(model, 'feature_names_in_'):
            X = X[model.feature_names_in_]
        y_pred = model.predict(X)

        # Confusion matrix
        print('y_true:', y_true[:20])
        print('y_pred:', y_pred[:20])
        cm = confusion_matrix(y_true, y_pred)
        print('Confusion matrix:\n', cm)
        if cm.shape != (2, 2):
            print('Confusion matrix is not 2x2, returning error message.')
            return jsonify({'error': f'Confusion matrix shape is {cm.shape}. Not enough class variety in data or predictions.'}), 400
        import matplotlib
        matplotlib.use('Agg')  # Ensure non-interactive backend
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Fraud', 'Fraud'], yticklabels=['Not Fraud', 'Fraud'], ax=ax)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        ax.set_title('Confusion Matrix')
        fig.tight_layout()
        buf = BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        print('Returning confusion matrix image with values:', cm)
        return jsonify({'image': img_base64})
    except Exception as e:
        print(f"Error in confusion_matrix_api: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# --- 3. Run the App ---
if __name__ == '__main__':
    # Runs the Flask server on http://127.0.0.1:5000
    app.run(debug=True)
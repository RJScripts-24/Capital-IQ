# Capital IQ - AI-Powered Financial Analyzer

An intelligent financial analysis tool that helps users understand their spending patterns, detect anomalies, and make informed financial decisions using AI.

## Features

### 📊 Financial Analysis
- Upload credit card transaction CSV files
- Detect fraudulent/anomalous transactions using machine learning
- Analyze spending patterns by category
- Generate personalized savings plans
- Visualize expenditure data with interactive charts

### 💬 AI Financial Assistant (Chatbot)
- Ask questions about your spending in natural language
- Get instant answers about spending amounts, categories, and comparisons
- Examples:
  - "How much did I spend on coffee last month vs this month?"
  - "What's my total spending?"
  - "How much did I spend on dining?"

### 🔮 What-If Simulator
- Simulate the impact of financial decisions on your savings
- See how purchases or spending changes affect your 6-month savings plan
- Examples:
  - "What happens to my 6-month savings plan if I buy a $1,000 laptop today?"
  - "How would cutting dining expenses by 50% affect my savings?"

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Gemini API key:
   - Get a Gemini Pro API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Edit the `.env` file and replace `your_gemini_api_key_here` with your actual API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

4. Ensure you have the ML model files:
   - Run `python train_model.py` if the `ml_assets/` directory is empty
   - The system uses sample data (`large_test_data.csv`) for AI queries when no user data is uploaded

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```

2. The backend will run on `http://127.0.0.1:5000`

3. The frontend will run on `http://localhost:3000`

## API Endpoints

### `/analyze` (POST)
Upload and analyze a CSV file with transaction data.

**Request:** Multipart form data with a `file` field containing the CSV.

**Response:** Analysis results including anomalies, expenditure breakdown, and savings recommendations.

### `/query` (POST)
Natural language query about financial data.

**Request:**
```json
{
  "query": "How much did I spend on coffee last month?"
}
```

**Response:**
```json
{
  "response": "You spent $45 last month and $62 this month on coffee.",
  "data": {
    "last_month": 45,
    "this_month": 62,
    "category": "coffee"
  }
}
```

### `/simulate` (POST)
Simulate financial scenarios.

**Request:**
```json
{
  "scenario": "What happens to my 6-month savings plan if I buy a $1,000 laptop today?"
}
```

**Response:**
```json
{
  "impact_description": "Purchasing a $1,000 laptop today would reduce your 6-month savings by approximately $167.",
  "original_6month_savings": "$2,500",
  "new_6month_savings": "$2,333",
  "monthly_change": "-$167",
  "recommendations": ["Consider saving for 2 more months before purchasing", "Look for deals or refurbished options"]
}
```

## Data Format

The application expects CSV files with the following columns:
- `Time`: Transaction timestamp (numeric)
- `Amount`: Transaction amount (numeric)
- `Category`: Spending category (string)
- `V1` through `V28`: Anonymized features for fraud detection

## Technologies Used

- **Backend:** Python, Flask, scikit-learn, pandas
- **Frontend:** React, Chart.js, Axios
- **AI:** Google Gemini Pro API
- **ML:** Random Forest for anomaly detection

## Security Notes

- The Gemini API key is stored in a `.env` file (not committed to version control)
- All API communications happen server-side to protect the API key
- User data is processed in-memory and not stored permanently

## Troubleshooting

### AI Features Not Working
- Ensure your Gemini API key is correctly set in the `.env` file
- Check that the API key has sufficient quota
- Verify internet connectivity for API calls

### Model Loading Errors
- Run `python train_model.py` to generate the required ML model files
- Ensure all files in `ml_assets/` directory are present

### Frontend Connection Issues
- Ensure the backend is running on port 5000
- Check CORS settings if making requests from different domains
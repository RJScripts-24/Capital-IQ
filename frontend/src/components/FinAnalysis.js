import React, { useState } from 'react';
import axios from 'axios';
import MetricsDisplay from './MetricsDisplay';
import ExpenditureChart from './ExpenditureChart';
import { jsPDF } from 'jspdf';
function FinAnalysis() {
    const [file, setFile] = useState(null);
    const [results, setResults] = useState(null);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    // Function to convert anomalies to CSV and trigger download
    const downloadAnomaliesCSV = () => {
        if (!results || !results.user_anomalies || results.user_anomalies.length === 0) {
            return;
        }
        
        // CSV Headers
        const headers = ['Time', 'Amount', 'Category'];
        
        // Convert anomaly data to CSV rows
        const csvRows = results.user_anomalies.map(anomaly => {
            const amount = typeof anomaly.Amount === 'number' ? anomaly.Amount.toFixed(2) : Number(anomaly.Amount).toFixed(2);
            const category = anomaly.Category || 'N/A';
            return `${anomaly.Time},${amount},"${category}"`;
        });
        
        // Combine headers and data
        const csvContent = [
            headers.join(','),
            ...csvRows
        ].join('\n');
        
        // Create a blob and download link
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        // Set up and trigger download
        link.setAttribute('href', url);
        link.setAttribute('download', 'anomalous_transactions.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Function to download Savings Planner as PDF
    const downloadSavingsPlannerPDF = () => {
        if (!results || !results.expenditure_analysis || !results.expenditure_analysis.savings_plan) {
            return;
        }
        
        const doc = new jsPDF();
        doc.setFontSize(16);
        doc.text('Savings Planner', 10, 20);
        doc.setFontSize(12);
        let y = 30;
        const savingsPlan = results.expenditure_analysis.savings_plan;
        
        if (Object.keys(savingsPlan).length > 0) {
            Object.entries(savingsPlan).forEach(([cat, suggestion]) => {
                doc.text(`- ${suggestion}`, 10, y);
                y += 10;
            });
        } else {
            doc.text('No specific savings suggestions at this time.', 10, y);
        }
        
        doc.save('savings_planner.pdf');
    };

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        // Reset results when a new file is chosen
        setResults(null);
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a CSV file first.');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        setIsLoading(true);
        setError('');
        setResults(null);

        try {
            // This URL points to your running Flask backend
            const response = await axios.post('http://127.0.0.1:5000/analyze', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setResults(response.data);
        } catch (err) {
            const errorMessage = err.response ? err.response.data.error + (err.response.data.details ? `: ${err.response.data.details}` : '') : 'An unexpected error occurred.';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="container">
            <header>
                <h1>AI-Powered Financial Analyzer</h1>
                <p>Upload your credit card transaction CSV to detect anomalies, analyze spending, and get a personalized savings plan.</p>
            </header>
            
            <form onSubmit={handleSubmit} className="upload-form">
                <input type="file" accept=".csv" onChange={handleFileChange} />
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Analyzing...' : 'Analyze Transactions'}
                </button>
            </form>

            {error && <p className="error-message">{error}</p>}
            
            {results && (
                <div className="results-container">
                    <MetricsDisplay performance={results.model_performance} />
                    
                    {results.expenditure_analysis && !results.expenditure_analysis.error && (
                         <div className="results-card">
                            <h3>Expenditure Analysis</h3>

                            {/* --- NEW PART START --- */}
                            {/* Conditionally render the chart if there is category data */}
                            {Object.keys(results.expenditure_analysis.spend_by_category).length > 0 ? (
                                <ExpenditureChart analysisData={results.expenditure_analysis} />
                            ) : (
                                <p>No category spending data to visualize.</p>
                            )}
                            {/* --- NEW PART END --- */}

                            <p><strong>Total Spend:</strong> ${results.expenditure_analysis.total_spend}</p>

                            <h4>Savings Planner:</h4>
                            {Object.keys(results.expenditure_analysis.savings_plan).length > 0 ? (
                                <ul>
                                   {Object.entries(results.expenditure_analysis.savings_plan).map(([cat, suggestion]) => (
                                        <li key={cat}>{suggestion}</li>
                                    ))}
                                </ul>
                            ) : <p>No specific savings suggestions at this time.</p>}
                            <div className="actions-container">
                                <button className="download-btn" onClick={downloadSavingsPlannerPDF}>
                                    <span className="download-icon">📄</span> Download Savings Planner as PDF
                                </button>
                            </div>
                        </div>
                    )}

                    <div className="results-card">
                        <h3>Detected Anomalies</h3>
                        {results.user_anomalies && results.user_anomalies.length > 0 ? (
                            <>
                                <p className="summary-text">
                                    Found <strong>{results.user_anomalies.length}</strong> potentially anomalous transaction(s). Please review the items below.
                                </p>
                                <table className="anomalies-table">
                                    <thead>
                                        <tr>
                                            <th>Time</th>
                                            <th>Amount ($)</th>
                                            <th>Category</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {results.user_anomalies.map((anomaly, index) => (
                                            <tr key={index}>
                                                <td>{anomaly.Time}</td>
                                                <td>{typeof anomaly.Amount === 'number' ? anomaly.Amount.toFixed(2) : Number(anomaly.Amount).toFixed(2)}</td>
                                                <td>{anomaly.Category || 'N/A'}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                <div className="actions-container">
                                    <button className="download-btn" onClick={downloadAnomaliesCSV}>
                                        <span className="download-icon">📥</span> Download Anomalies as CSV
                                    </button>
                                </div>
                            </>
                        ) : (
                            <p>No potential anomalies were detected in your file.</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default FinAnalysis;
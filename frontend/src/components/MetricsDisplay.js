import React from 'react';
import 'katex/dist/katex.min.css';
import { BlockMath, InlineMath } from 'react-katex';

// This is a dedicated component just for displaying the model's performance.
function MetricsDisplay({ performance }) {
    if (!performance) return null;

    const { tp, tn, fp, fn, accuracy, precision, recall, f1_score, specificity, mcc } = performance;
    
    // Add null/undefined checks and provide fallback values
    const safeF1Score = f1_score !== undefined ? f1_score : null;
    const safeSpecificity = specificity !== undefined ? specificity : null;
    const safeMcc = mcc !== undefined ? mcc : null;

    return (
        <div className="results-card">
            <h3>Model Performance Metrics</h3>
            <p>These metrics show the model's effectiveness, calculated on a standard test dataset.</p>

            <h4>Metric Results</h4>
            <div className="calculation"><strong>Accuracy:</strong> {accuracy.toFixed(4)}</div>
            <div className="calculation"><strong>Precision:</strong> {precision.toFixed(4)}</div>
            <div className="calculation"><strong>Recall (Sensitivity):</strong> {recall.toFixed(4)}</div>
            {safeF1Score !== null && (
                <div className="calculation"><strong>F1-Score:</strong> {safeF1Score.toFixed(4)}</div>
            )}
            {safeSpecificity !== null && (
                <div className="calculation"><strong>Specificity:</strong> {safeSpecificity.toFixed(4)}</div>
            )}
            {safeMcc !== null && (
                <div className="calculation"><strong>Matthews Corr. Coeff. (MCC):</strong> {safeMcc.toFixed(4)}</div>
            )}
        </div>
    );
}

export default MetricsDisplay;
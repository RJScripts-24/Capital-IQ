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
            
            <h4>Confusion Matrix</h4>
            <table className="confusion-matrix">
                <thead>
                    <tr>
                        <th></th>
                        <th>Predicted Positive (Fraud)</th>
                        <th>Predicted Negative (Normal)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th>Actual Positive</th>
                        <td className="true-positive">True Positive (TP): {tp}</td>
                        <td className="false-negative">False Negative (FN): {fn}</td>
                    </tr>
                    <tr>
                        <th>Actual Negative</th>
                        <td className="false-positive">False Positive (FP): {fp}</td>
                        <td className="true-negative">True Negative (TN): {tn}</td>
                    </tr>
                </tbody>
            </table>

            <h4>Metric Calculations</h4>
            <div className="calculation">
                <strong>Accuracy:</strong> The proportion of all predictions that were correct.
                <BlockMath math={`\\text{Accuracy} = \\frac{TP + TN}{TP + TN + FP + FN} = \\frac{${tp} + ${tn}}{${tp} + ${tn} + ${fp} + ${fn}} \\approx ${accuracy.toFixed(4)}`} />
            </div>
            <div className="calculation">
                <strong>Precision:</strong> Of all the transactions we predicted as fraud, how many were actually fraud.
                <BlockMath math={`\\text{Precision} = \\frac{TP}{TP + FP} = \\frac{${tp}}{${tp} + ${fp}} \\approx ${precision.toFixed(4)}`} />
            </div>
            <div className="calculation">
                <strong>Recall (Sensitivity):</strong> Of all the actual fraud transactions, how many did we correctly identify.
                <BlockMath math={`\\text{Recall} = \\frac{TP}{TP + FN} = \\frac{${tp}}{${tp} + ${fn}} \\approx ${recall.toFixed(4)}`} />
            </div>

            {safeF1Score !== null && (
                <div className="calculation">
                    <strong>F1-Score:</strong> A balanced measure of Precision and Recall, great for imbalanced data.
                    <BlockMath math={`\\text{F1-Score} = 2 \\times \\frac{\\text{Precision} \\times \\text{Recall}}{\\text{Precision} + \\text{Recall}} \\approx ${safeF1Score.toFixed(4)}`} />
                </div>
            )}

            {safeSpecificity !== null && (
                <div className="calculation">
                    <strong>Specificity:</strong> How well the model identifies legitimate (non-anomalous) transactions.
                    <BlockMath math={`\\text{Specificity} = \\frac{TN}{TN + FP} = \\frac{${tn}}{${tn} + ${fp}} \\approx ${safeSpecificity.toFixed(4)}`} />
                </div>
            )}

            {safeMcc !== null && (
                <div className="calculation">
                    <strong>Matthews Corr. Coeff. (MCC):</strong> A robust score from -1 to +1 summarizing the model's quality on imbalanced data.
                    {/* This formula is long, so we put it on a separate line */}
                    <BlockMath math={`\\text{MCC} = \\frac{(TP \\times TN) - (FP \\times FN)}{\\sqrt{(TP+FP)(TP+FN)(TN+FP)(TN+FN)}}`} />
                    <p>Result: <InlineMath math={`${safeMcc.toFixed(4)}`} /></p>
                </div>
            )}
        </div>
    );
}

export default MetricsDisplay;
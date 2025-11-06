import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

function WhatIfSimulator() {
    const [scenario, setScenario] = useState('');
    const [simulation, setSimulation] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!scenario.trim()) return;

        setIsLoading(true);
        setError('');
        setSimulation(null);

        try {
            const result = await axios.post(`${API_URL}/simulate`, {
                scenario: scenario
            });
            setSimulation(result.data);
        } catch (err) {
            const errorMessage = err.response ? err.response.data.error : 'An unexpected error occurred.';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="simulator-container">
            <h3>🔮 What-If Simulator</h3>
            <p>See how major financial decisions impact your savings plan!</p>

            <form onSubmit={handleSubmit} className="simulator-form">
                <div className="input-group">
                    <textarea
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value)}
                        placeholder="e.g., What happens to my 6-month savings plan if I buy a $1,000 laptop today?"
                        rows="3"
                        disabled={isLoading}
                    />
                    <button type="submit" disabled={isLoading}>
                        {isLoading ? 'Simulating...' : 'Simulate'}
                    </button>
                </div>
            </form>

            {error && <p className="error-message">{error}</p>}

            {simulation && !simulation.error && (
                <div className="simulation-results">
                    <h4>Simulation Results:</h4>
                    <div className="result-card">
                        <p><strong>Impact:</strong> {simulation.impact_description}</p>
                        <p><strong>Original 6-month savings:</strong> ${simulation.original_6month_savings}</p>
                        <p><strong>New 6-month savings:</strong> ${simulation.new_6month_savings}</p>
                        <p><strong>Monthly change:</strong> ${simulation.monthly_change}</p>
                    </div>

                    {simulation.recommendations && simulation.recommendations.length > 0 && (
                        <div className="recommendations">
                            <h4>Recommendations:</h4>
                            <ul>
                                {simulation.recommendations.map((rec, index) => (
                                    <li key={index}>{rec}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            <div className="example-scenarios">
                <h4>Example Scenarios:</h4>
                <ul>
                    <li>"What happens to my 6-month savings plan if I buy a $1,000 laptop today?"</li>
                    <li>"How would cutting dining expenses by 50% affect my savings?"</li>
                    <li>"What if I start saving $200 more per month?"</li>
                    <li>"Impact of a $500 emergency expense on my budget"</li>
                </ul>
            </div>
        </div>
    );
}

export default WhatIfSimulator;
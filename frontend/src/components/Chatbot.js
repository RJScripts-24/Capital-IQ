import React, { useState } from 'react';
import axios from 'axios';

function Chatbot() {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsLoading(true);
        setError('');
        setResponse('');

        try {
            const result = await axios.post('http://127.0.0.1:5000/query', {
                query: query
            });
            setResponse(result.data.response || JSON.stringify(result.data, null, 2));
        } catch (err) {
            const errorMessage = err.response ? err.response.data.error : 'An unexpected error occurred.';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chatbot-container">
            <h3>💬 AI Financial Assistant</h3>
            <p>Ask questions about your spending in plain English!</p>

            <form onSubmit={handleSubmit} className="chatbot-form">
                <div className="input-group">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="e.g., How much did I spend on coffee last month?"
                        disabled={isLoading}
                    />
                    <button type="submit" disabled={isLoading}>
                        {isLoading ? 'Thinking...' : 'Ask'}
                    </button>
                </div>
            </form>

            {error && <p className="error-message">{error}</p>}

            {response && (
                <div className="chatbot-response">
                    <h4>Response:</h4>
                    <p>{response}</p>
                </div>
            )}

            <div className="example-queries">
                <h4>Example Queries:</h4>
                <ul>
                    <li>"How much did I spend on coffee last month vs this month?"</li>
                    <li>"What's my total spending?"</li>
                    <li>"How much did I spend on dining?"</li>
                    <li>"How many anomalous transactions do I have?"</li>
                </ul>
            </div>
        </div>
    );
}

export default Chatbot;
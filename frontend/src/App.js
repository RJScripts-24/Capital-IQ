import React, { useState } from 'react';
import FinAnalysis from './components/FinAnalysis';
import './App.css';

function App() {
  // We'll lift the results state up so we can pass it to left/right columns
  const [results, setResults] = useState(null);
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="App full-screen-app">
      <div className="main-split-layout">
        {/* Left: MetricsDisplay (and maybe upload form) */}
        <div className="left-panel">
          <FinAnalysis
            results={results}
            setResults={setResults}
            file={file}
            setFile={setFile}
            error={error}
            setError={setError}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
            panel="left"
          />
        </div>
        {/* Right: Expenditure Analysis, Anomalies, etc. */}
        <div className="right-panel">
          <FinAnalysis
            results={results}
            setResults={setResults}
            file={file}
            setFile={setFile}
            error={error}
            setError={setError}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
            panel="right"
          />
        </div>
      </div>
    </div>
  );
}

export default App;
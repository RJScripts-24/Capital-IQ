import React from 'react';
import FinAnalysis from './components/FinAnalysis'; // We import the component that has all our logic
import './App.css'; // We import the main stylesheet for the application

/**
 * This is the root component of the React application.
 * It's a functional component that returns the main layout of the app.
 */
function App() {
  // The component returns a single div with the className "App",
  // which serves as the main container. Inside this container,
  // we render the FinAnalysis component, which holds all the
  // user interface for file uploading and results display.
  return (
    <div className="App">
      <FinAnalysis />
    </div>
  );
}

// We export the App component so it can be used by index.js,
// which is the entry point that renders the entire application
// into the DOM (specifically into the <div id="root"></div> in index.html).
export default App;
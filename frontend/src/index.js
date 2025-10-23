import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css'; // We import the main stylesheet we already created
import App from './App'; // We import the main App component

/**
 * This is the entry point of your React application.
 */

// 1. Find the HTML element with the ID of 'root' in your public/index.html file.
//    This is where our entire application will be displayed.
const rootElement = document.getElementById('root');

// 2. Create a "root" for our React application, which will manage the content
//    of the rootElement.
const root = ReactDOM.createRoot(rootElement);

// 3. Tell React to render our main <App /> component inside this root.
//    <React.StrictMode> is a helper that warns about potential problems in the app.
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
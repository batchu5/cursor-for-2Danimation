import { useState } from 'react'
import './App.css'
import {BrowserRouter as Router,Routes,Route, Navigate} from "react-router-dom";
import DashBoard from './components/dashboard' 
import LandingPage from './components/LandingPage';
import CallbackPage from './components/CallbackPage';
import { useAuth0 } from '@auth0/auth0-react';

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0();
  
  if (isLoading) {
    return (
      <div className="bg-neutral-900 h-screen w-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <svg
            className="animate-spin h-10 w-10 text-purple-400"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          <span className="text-neutral-400 text-lg">Loading...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    loginWithRedirect();
    return null;
  }

  return children;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<LandingPage />} />
        <Route path='/callback' element={<CallbackPage />} />
        <Route path='/dashboard' element={
          <ProtectedRoute>
            <DashBoard />
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  )
}

export default App

// Main App with routing
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LeadForm from './components/LeadForm';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LeadDetail from './pages/LeadDetail';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LeadForm />} />
        <Route path="/lead-form" element={<LeadForm />} />
        
        {/* Auth routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected routes */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/lead/:id" element={<LeadDetail />} />
        
        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
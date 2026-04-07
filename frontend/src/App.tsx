// Main App with routing for all user roles
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LeadForm from './components/LeadForm';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LeadDetail from './pages/LeadDetail';
import BranchManager from './pages/BranchManager';
import ComplianceAudit from './pages/ComplianceAudit';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LeadForm />} />
        <Route path="/lead-form" element={<LeadForm />} />
        
        {/* Auth routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected routes - Sales Rep */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/lead/:id" element={<LeadDetail />} />
        
        {/* Protected routes - Branch Manager */}
        <Route path="/branch-manager" element={<BranchManager />} />
        
        {/* Protected routes - Compliance Officer */}
        <Route path="/compliance" element={<ComplianceAudit />} />
        
        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
// Login Page with Role-Based Routing
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { authApi, saveTokens, getAccessToken } from '../services/api';
import { Lock, User, AlertCircle } from 'lucide-react';

export function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Role-based redirect mapping
  const getRedirectPath = (role: string): string => {
    switch (role) {
      case 'SALES_REP':
        return '/dashboard';
      case 'BRANCH_MANAGER':
        return '/branch-manager';
      case 'COMPLIANCE_OFFICER':
        return '/compliance';
      case 'IT_ADMIN':
        return '/branch-manager'; // IT Admin sees branch manager view
      default:
        return '/dashboard';
    }
  };

  const getRoleLabel = (role: string): string => {
    switch (role) {
      case 'SALES_REP':
        return 'Sales Representative Portal';
      case 'BRANCH_MANAGER':
        return 'Branch Manager Portal';
      case 'COMPLIANCE_OFFICER':
        return 'Compliance Officer Portal';
      case 'IT_ADMIN':
        return 'IT Administrator Portal';
      default:
        return 'Sales Representative Portal';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Step 1: Login and get tokens
      const tokens = await authApi.login({ username, password });
      saveTokens(tokens);
      
      // Step 2: Get current user info to determine role
      const token = getAccessToken();
      if (token) {
        try {
          const user = await authApi.getCurrentUser();
          const redirectPath = getRedirectPath(user.role);
          navigate(redirectPath);
        } catch {
          // If we can't get user info, default to dashboard
          navigate('/dashboard');
        }
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl font-bold">ST</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">STBank LeadGen</h1>
          <p className="text-gray-600 mt-1"> Laos Lead Generation Platform</p>
        </div>

        {/* Role Info Cards */}
        <div className="mb-6 space-y-2">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
            <p className="font-medium text-blue-800">Sales Rep (sales@stbank.la)</p>
            <p className="text-blue-600">Password: sales123</p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm">
            <p className="font-medium text-green-800">Branch Manager (manager@stbank.la)</p>
            <p className="text-green-600">Password: manager123</p>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-sm">
            <p className="font-medium text-purple-800">Compliance (compliance@stbank.la)</p>
            <p className="text-purple-600">Password: compliance123</p>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm">
            <p className="font-medium text-red-800">IT Admin (admin@stbank.la)</p>
            <p className="text-red-600">Password: admin123</p>
          </div>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-card p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Sign In</h2>

          {error && (
            <div className="mb-4 p-3 bg-error/10 border border-error/20 rounded-lg flex items-center gap-2 text-error text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Username or Email"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              leftIcon={<User className="w-5 h-5" />}
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              leftIcon={<Lock className="w-5 h-5" />}
              required
            />

            <Button
              type="submit"
              className="w-full"
              size="lg"
              isLoading={isLoading}
            >
              Sign In
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            Forgot your password? Contact IT administrator.
          </p>
        </div>

        <p className="mt-6 text-center text-xs text-gray-400">
          &copy; 2026 STBank Laos. Authorized access only.
        </p>
      </div>
    </div>
  );
}

export default Login;

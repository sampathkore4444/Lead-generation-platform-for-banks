import React, { useState, useEffect } from 'react';
import { Shield, RefreshCw } from 'lucide-react';

interface CaptchaWidgetProps {
  onVerify: (valid: boolean) => void;
}

export const CaptchaWidget: React.FC<CaptchaWidgetProps> = ({ onVerify }) => {
  const [token, setToken] = useState<string>('');
  const [question, setQuestion] = useState<string>('');
  const [answer, setAnswer] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [verified, setVerified] = useState<boolean>(false);

  const fetchCaptcha = async () => {
    setLoading(true);
    setError('');
    setAnswer('');
    setVerified(false);
    
    try {
      const response = await fetch('/api/v1/mfa/captcha');
      const data = await response.json();
      
      if (data.token) {
        setToken(data.token);
        setQuestion(data.question);
      }
    } catch (err) {
      setError('Failed to load CAPTCHA');
      console.error('CAPTCHA error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCaptcha();
  }, []);

  const handleVerify = async () => {
    if (!answer.trim()) {
      setError('Please enter the answer');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/mfa/captcha/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, answer })
      });
      
      const data = await response.json();
      
      if (data.valid) {
        setVerified(true);
        onVerify(true);
      } else {
        setError('Incorrect answer. Please try again.');
        fetchCaptcha(); // Get new challenge
      }
    } catch (err) {
      setError('Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleVerify();
    }
  };

  if (verified) {
    return (
      <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
        <Shield className="w-5 h-5 text-green-600" />
        <span className="text-green-700 text-sm">Verified</span>
      </div>
    );
  }

  return (
    <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
      <div className="flex items-center gap-2 mb-3">
        <Shield className="w-4 h-4 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">Security Check</span>
      </div>
      
      {question && (
        <div>
          <div className="mb-3">
            <label className="block text-sm text-gray-600 mb-1">
              {question}
            </label>
            <input
              type="number"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyPress={handleKeyPress}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter answer"
              disabled={loading}
            />
          </div>
          
          {error && (
            <p className="text-red-500 text-sm mb-3">{error}</p>
          )}
          
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleVerify}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Verifying...' : 'Verify'}
            </button>
            
            <button
              type="button"
              onClick={fetchCaptcha}
              disabled={loading}
              className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
              title="Get new challenge"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CaptchaWidget;

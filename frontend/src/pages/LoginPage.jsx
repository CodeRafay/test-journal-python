import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import NumericKeypad from '../components/NumericKeypad';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Shield, Lock } from 'lucide-react';

const LoginPage = () => {
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = (role, errorMessage = null) => {
    if (role === 'admin') {
      localStorage.setItem('userRole', 'admin');
      navigate('/admin');
    } else if (role === 'viewer') {
      localStorage.setItem('userRole', 'viewer');
      navigate('/shared');
    } else {
      setError(errorMessage || 'Invalid password. Please try again.');
      setTimeout(() => setError(''), 5000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="p-3 bg-red-600/20 rounded-full">
              <Shield className="w-8 h-8 text-red-500" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-100 mb-2">
            Journal Access
          </h1>
          <p className="text-gray-400">
            Enter your 8-digit access code
          </p>
        </div>

        {/* Login Card */}
        <Card className="bg-gray-800/30 border-gray-700 shadow-2xl">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center space-x-2 text-gray-100">
              <Lock className="w-5 h-5 text-red-500" />
              <span>Secure Login</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <NumericKeypad onLogin={handleLogin} error={error} />
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>Protected by secure access codes</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
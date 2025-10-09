import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthHeader from '../components/auth/AuthHeader';
import AuthFooter from '../components/auth/AuthFooter';

const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!email) {
      setError('Please enter your email');
      return;
    }

    setLoading(true);

    try {
      // TODO: Implement password reset API call
      // await authService.forgotPassword(email);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess(true);
      setTimeout(() => {
        navigate('/auth/login');
      }, 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error sending reset link. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/auth/login');
  };

  return (
    <div className="min-h-screen bg-[#eaf4fd] flex flex-col">
      <AuthHeader />

      <main className="flex-1 flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-7xl flex gap-12">
          {/* Left Side - Marketing Content */}
          <div className="flex-1 flex flex-col justify-center">
            <h1 className="font-bold text-[48px] leading-tight mb-4">
              <span className="text-gray-900">Lost your</span>{' '}
              <span className="text-blue-600">way?</span>
            </h1>
            <p className="font-medium text-[22px] text-gray-900">
              No worries — we'll send a reset link to your email.
            </p>
          </div>

          {/* Right Side - Forgot Password Form */}
          <div className="w-full max-w-[636px] bg-white rounded-xl shadow-lg p-12">
            <h2 className="font-bold text-[48px] text-gray-900 mb-4">Forgot password?</h2>
            <p className="text-[16px] text-gray-700 mb-8">
              Enter your email to reset your password
            </p>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                {error}
              </div>
            )}

            {success && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-600 text-sm">
                Reset link sent! Check your email. Redirecting to login...
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email */}
              <div>
                <label className="font-semibold text-[16px] text-gray-900 block mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 transition"
                  placeholder="your@email.com"
                  required
                  disabled={success}
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={loading || success}
                  className="flex-1 px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold text-[16px] hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Sending...' : 'Sumbit'}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  disabled={loading || success}
                  className="flex-1 px-6 py-2.5 border border-gray-200 text-gray-900 rounded-lg font-semibold text-[16px] hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>

      <AuthFooter />
    </div>
  );
};

export default ForgotPasswordPage;


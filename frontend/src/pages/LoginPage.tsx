import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import AuthHeader from '../components/auth/AuthHeader';
import AuthFooter from '../components/auth/AuthFooter';
import googleIcon from '../designSvg/google.svg';
import appleIcon from '../designSvg/apple.svg';
import eyeOpenIcon from '../designSvg/eye-open.svg';
import eyeClosedIcon from '../designSvg/eye-closed.svg';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      const response = await authService.login(email, password);
      login(response.access_token, response.user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login error. Please check your email and password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#eaf4fd] flex flex-col">
      <AuthHeader currentPage="login" />

      <main className="flex-1 flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-7xl flex gap-12">
          {/* Left Side - Marketing Content */}
          <div className="flex-1 flex flex-col justify-center">
            <h1 className="font-bold text-[48px] leading-tight mb-4">
              <span className="text-blue-600">Found</span>{' '}
              <span className="text-gray-900">something you liked?</span>
            </h1>
            <p className="font-medium text-[22px] text-gray-900">
              Log in — your perfect apartment might be here already.
            </p>
          </div>

          {/* Right Side - Login Form */}
          <div className="w-full max-w-[636px] bg-white rounded-xl shadow-lg p-12">
            <h2 className="font-bold text-[48px] text-gray-900 mb-8">Log in</h2>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                {error}
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
                />
              </div>

              {/* Password */}
              <div>
                <label className="font-semibold text-[16px] text-gray-900 block mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2.5 pr-12 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 transition"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2"
                  >
                    <img
                      src={showPassword ? eyeOpenIcon : eyeClosedIcon}
                      alt="Toggle password visibility"
                      className="w-5 h-5"
                    />
                  </button>
                </div>
                <div className="mt-2 text-right">
                  <Link
                    to="/auth/forgot-password"
                    className="font-bold text-[12px] text-blue-600 hover:underline"
                  >
                    Forgot Password?
                  </Link>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold text-[16px] hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Logging in...' : 'Log in'}
              </button>

              {/* Divider */}
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center">
                  <span className="px-4 bg-white text-[16px] text-gray-900">Or with</span>
                </div>
              </div>

              {/* Social Buttons */}
              <div className="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  className="flex items-center justify-center gap-2 px-6 py-2.5 border border-gray-200 rounded-lg font-semibold text-[16px] text-gray-900 hover:bg-gray-50 transition"
                >
                  <img src={googleIcon} alt="Google" className="w-6 h-6" />
                  <span>Log in with Google</span>
                </button>
                <button
                  type="button"
                  className="flex items-center justify-center gap-2 px-6 py-2.5 border border-gray-200 rounded-lg font-semibold text-[16px] text-gray-900 hover:bg-gray-50 transition"
                >
                  <img src={appleIcon} alt="Apple" className="w-6 h-6" />
                  <span>Log in with Apple</span>
                </button>
              </div>
            </form>

            {/* Sign Up Link */}
            <p className="mt-6 text-center text-[12px] text-gray-700">
              Not a member yet?{' '}
              <Link to="/auth/signup" className="font-bold text-blue-600 hover:underline">
                Sing up
              </Link>
            </p>
          </div>
        </div>
      </main>

      <AuthFooter />
    </div>
  );
};

export default LoginPage;


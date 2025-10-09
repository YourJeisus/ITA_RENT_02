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

const SignUpPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showRepeatPassword, setShowRepeatPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!email || !password || !repeatPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (password !== repeatPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Use 8 or more characters with a mix of letters, numbers & symbols');
      return;
    }

    if (!acceptTerms) {
      setError('Please accept the terms');
      return;
    }

    setLoading(true);

    try {
      await authService.register({
        email,
        password,
        first_name: '',
        last_name: '',
      });

      // Auto login after registration
      const loginResponse = await authService.login(email, password);
      login(loginResponse.access_token, loginResponse.user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#eaf4fd] flex flex-col">
      <AuthHeader currentPage="signup" />

      <main className="flex-1 flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-7xl flex gap-12">
          {/* Left Side - Marketing Content */}
          <div className="flex-1 flex flex-col justify-center">
            <h1 className="font-bold text-[48px] leading-tight text-gray-900 mb-4">
              <span className="text-blue-600">Apartments</span> won't find themselves
            </h1>
            <p className="font-medium text-[22px] text-gray-900">
              Sign up and I'll start the search.
            </p>
          </div>

          {/* Right Side - Sign Up Form */}
          <div className="w-full max-w-[636px] bg-white rounded-xl shadow-lg p-12">
            <h2 className="font-bold text-[48px] text-gray-900 mb-8">Sign up</h2>

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
                <p className="mt-2 text-[12px] text-gray-700">
                  Use 8 or more characters with a mix of letters, numbers & symbols.
                </p>
              </div>

              {/* Repeat Password */}
              <div>
                <label className="font-semibold text-[16px] text-gray-900 block mb-2">
                  Repeat password
                </label>
                <div className="relative">
                  <input
                    type={showRepeatPassword ? 'text' : 'password'}
                    value={repeatPassword}
                    onChange={(e) => setRepeatPassword(e.target.value)}
                    className="w-full px-4 py-2.5 pr-12 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 transition"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowRepeatPassword(!showRepeatPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2"
                  >
                    <img
                      src={showRepeatPassword ? eyeOpenIcon : eyeClosedIcon}
                      alt="Toggle password visibility"
                      className="w-5 h-5"
                    />
                  </button>
                </div>
              </div>

              {/* Terms Checkbox */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="acceptTerms"
                  checked={acceptTerms}
                  onChange={(e) => setAcceptTerms(e.target.checked)}
                  className="w-5 h-5 rounded border-gray-200 text-blue-600 focus:ring-blue-600"
                />
                <label htmlFor="acceptTerms" className="font-normal text-[16px] text-gray-900">
                  I accept the <span className="text-blue-600 cursor-pointer hover:underline">Term</span>
                </label>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold text-[16px] hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating account...' : 'Sign up'}
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
                  <span>Sign up with Google</span>
                </button>
                <button
                  type="button"
                  className="flex items-center justify-center gap-2 px-6 py-2.5 border border-gray-200 rounded-lg font-semibold text-[16px] text-gray-900 hover:bg-gray-50 transition"
                >
                  <img src={appleIcon} alt="Apple" className="w-6 h-6" />
                  <span>Sign up with Apple</span>
                </button>
              </div>
            </form>

            {/* Login Link */}
            <p className="mt-6 text-center text-[12px] text-gray-700">
              Already have an account?{' '}
              <Link to="/auth/login" className="font-bold text-blue-600 hover:underline">
                Log In
              </Link>
            </p>
          </div>
        </div>
      </main>

      <AuthFooter />
    </div>
  );
};

export default SignUpPage;


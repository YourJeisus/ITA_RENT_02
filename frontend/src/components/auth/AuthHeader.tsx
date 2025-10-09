import React from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";

interface AuthHeaderProps {
  currentPage?: "login" | "signup" | "settings";
}

const AuthHeader: React.FC<AuthHeaderProps> = ({ currentPage }) => {
  const { isAuthenticated } = useAuthStore();

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-8 h-[72px] flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="font-extrabold text-[22px] text-blue-600">
          RentAg
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-8">
          <Link
            to="/search"
            className="font-medium text-[16px] text-gray-900 hover:text-blue-600 transition"
          >
            Apartment search
          </Link>
          <Link
            to="#how-it-works"
            className="font-medium text-[16px] text-gray-900 hover:text-blue-600 transition"
          >
            How it works
          </Link>
          <Link
            to="#contact"
            className="font-medium text-[16px] text-gray-900 hover:text-blue-600 transition"
          >
            Contact
          </Link>
          <Link
            to="#faq"
            className="font-medium text-[16px] text-gray-900 hover:text-blue-600 transition"
          >
            FAQ
          </Link>
        </nav>

        {/* Auth Buttons */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Link
              to="/settings"
              className={`px-6 py-2 rounded-lg font-semibold text-[16px] transition ${
                currentPage === "settings"
                  ? "bg-blue-600 text-white"
                  : "border border-gray-200 text-gray-900 hover:bg-gray-50"
              }`}
            >
              Settings & Filters
            </Link>
          ) : (
            <>
              <Link
                to="/auth/login"
                className={`px-6 py-2 rounded-lg font-semibold text-[16px] transition ${
                  currentPage === "login"
                    ? "bg-blue-600 text-white"
                    : "border border-gray-200 text-gray-900 hover:bg-gray-50"
                }`}
              >
                Log in
              </Link>
              <Link
                to="/auth/signup"
                className={`px-6 py-2 rounded-lg font-semibold text-[16px] transition ${
                  currentPage === "signup"
                    ? "bg-blue-600 text-white"
                    : "border border-gray-200 text-gray-900 hover:bg-gray-50"
                }`}
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default AuthHeader;

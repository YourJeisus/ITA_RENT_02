import { create } from 'zustand';
import { User } from '../types';
import { authService } from '../services/authService';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  checkAuth: () => Promise<void>;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: (token: string, user: User) => {
    authService.setAuthToken(token);
    set({ user, isAuthenticated: true });
  },

  logout: () => {
    authService.logout();
    set({ user: null, isAuthenticated: false });
  },

  setUser: (user: User) => {
    set({ user });
  },

  checkAuth: async () => {
    const token = authService.getAuthToken();
    if (token) {
      try {
        authService.setAuthToken(token);
        const user = await authService.getCurrentUser();
        set({ user, isAuthenticated: true, isLoading: false });
      } catch (error) {
        authService.logout();
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } else {
      set({ isLoading: false });
    }
  },
}));

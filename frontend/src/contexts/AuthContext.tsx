import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { User } from '../types';
import { authService, LoginCredentials, RegisterData, AuthResponse } from '../services/authService';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isGuest: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (registerData: RegisterData) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  loginWithApple: () => Promise<void>;
  loginAsGuest: () => Promise<void>;
  logout: () => Promise<void>;
  deleteAccount: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
  refreshAccessToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGuest, setIsGuest] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);

  useEffect(() => {
    loadUserFromStorage();
  }, []);

  const loadUserFromStorage = async () => {
    try {
      const [userData, storedAccessToken, storedRefreshToken] = await Promise.all([
        AsyncStorage.getItem('user'),
        AsyncStorage.getItem('accessToken'),
        AsyncStorage.getItem('refreshToken')
      ]);

      if (userData && storedAccessToken) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setAccessToken(storedAccessToken);
        setRefreshToken(storedRefreshToken);
        setIsGuest(parsedUser.isGuest || false);

        // Check if token is expired and refresh if needed
        if (authService.isTokenExpired(storedAccessToken) && storedRefreshToken) {
          try {
            await refreshAccessToken();
          } catch (error) {
            console.error('Failed to refresh token:', error);
            // Clear invalid tokens
            await clearAuthData();
          }
        }
      } else {
        // No user data found - no persistent guest sessions
        // Guest users should always start fresh when app is opened
        setIsGuest(false);
      }
    } catch (error) {
      console.error('Error loading user from storage:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveUserToStorage = async (userData: User) => {
    try {
      await AsyncStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      console.error('Error saving user to storage:', error);
    }
  };

  const saveTokensToStorage = async (accessToken: string, refreshToken: string) => {
    try {
      await Promise.all([
        AsyncStorage.setItem('accessToken', accessToken),
        AsyncStorage.setItem('refreshToken', refreshToken)
      ]);
    } catch (error) {
      console.error('Error saving tokens to storage:', error);
    }
  };

  const clearAuthData = async () => {
    try {
      // Import storageService here to avoid circular dependency
      const { storageService } = await import('../utils/storage');
      
      await Promise.all([
        AsyncStorage.removeItem('user'),
        AsyncStorage.removeItem('accessToken'),
        AsyncStorage.removeItem('refreshToken'),
        AsyncStorage.removeItem('isGuest'),
        // Clear all analysis data to ensure fresh start
        storageService.clear()
      ]);
      setUser(null);
      setAccessToken(null);
      setRefreshToken(null);
      setIsGuest(false);
    } catch (error) {
      console.error('Error clearing auth data:', error);
    }
  };

  const refreshAccessToken = async () => {
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await authService.refreshToken(refreshToken);
      setAccessToken(response.access_token);
      await AsyncStorage.setItem('accessToken', response.access_token);
      
      // Update user data if it changed
      if (response.user) {
        const userData: User = {
          id: response.user.user_id,
          email: response.user.email,
          displayName: response.user.display_name,
          isGuest: false,
          isPremium: response.user.is_premium,
          streakCount: response.user.streak_count,
          createdAt: new Date(response.user.created_at),
          lastActive: new Date(response.user.last_active),
        };
        setUser(userData);
        await saveUserToStorage(userData);
      }
    } catch (error) {
      console.error('Error refreshing access token:', error);
      await clearAuthData();
      throw error;
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await authService.login({ email, password });
      
      const userData: User = {
        id: response.user.user_id,
        email: response.user.email,
        displayName: response.user.display_name,
        isGuest: false,
        isPremium: response.user.is_premium,
        streakCount: response.user.streak_count,
        createdAt: new Date(response.user.created_at),
        lastActive: new Date(response.user.last_active),
      };
      
      setUser(userData);
      setAccessToken(response.access_token);
      setRefreshToken(response.refresh_token || null);
      setIsGuest(false);
      
      await Promise.all([
        saveUserToStorage(userData),
        saveTokensToStorage(response.access_token, response.refresh_token || '')
      ]);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (registerData: RegisterData) => {
    try {
      setIsLoading(true);
      const response = await authService.register(registerData);
      
      const userData: User = {
        id: response.user.user_id,
        email: response.user.email,
        displayName: response.user.display_name,
        isGuest: false,
        isPremium: response.user.is_premium,
        streakCount: response.user.streak_count,
        createdAt: new Date(response.user.created_at),
        lastActive: new Date(response.user.last_active),
      };
      
      setUser(userData);
      setAccessToken(response.access_token);
      setRefreshToken(response.refresh_token || null);
      setIsGuest(false);
      
      await Promise.all([
        saveUserToStorage(userData),
        saveTokensToStorage(response.access_token, response.refresh_token || '')
      ]);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    try {
      setIsLoading(true);
      // TODO: Implement Google Sign-In
      const userData: User = {
        id: 'google_temp_id',
        email: 'user@gmail.com',
        displayName: 'Google User',
        photoURL: 'https://via.placeholder.com/150',
        isGuest: false,
        isPremium: false,
        streakCount: 0,
        createdAt: new Date(),
        lastActive: new Date(),
      };
      
      setUser(userData);
      setIsGuest(false);
      await saveUserToStorage(userData);
    } catch (error) {
      console.error('Google login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithApple = async () => {
    try {
      setIsLoading(true);
      // TODO: Implement Apple Sign-In
      const userData: User = {
        id: 'apple_temp_id',
        email: 'user@privaterelay.appleid.com',
        displayName: 'Apple User',
        isGuest: false,
        isPremium: false,
        streakCount: 0,
        createdAt: new Date(),
        lastActive: new Date(),
      };
      
      setUser(userData);
      setIsGuest(false);
      await saveUserToStorage(userData);
    } catch (error) {
      console.error('Apple login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loginAsGuest = async () => {
    try {
      setIsLoading(true);
      
      // Clear any existing data first to ensure fresh guest session
      const { storageService } = await import('../utils/storage');
      await storageService.clear();
      
      const guestId = `guest_${Date.now()}`;
      const userData: User = {
        id: guestId,
        displayName: 'Guest User',
        isGuest: true,
        isPremium: false,
        streakCount: 0,
        createdAt: new Date(),
        lastActive: new Date(),
      };
      
      setUser(userData);
      setIsGuest(true);
      // Don't save guest session to storage - guests should always start fresh
      // await AsyncStorage.setItem('isGuest', 'true');
      // await saveUserToStorage(userData);
    } catch (error) {
      console.error('Guest login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      
      // If we have tokens, try to logout from server
      if (accessToken && refreshToken) {
        try {
          await authService.logout(accessToken, refreshToken);
        } catch (error) {
          console.error('Server logout failed:', error);
          // Continue with local logout even if server logout fails
        }
      }
      
      await clearAuthData();
      
      // Also clear analysis data to ensure fresh start
      try {
        const { storageService } = await import('../utils/storage');
        await storageService.clear();
      } catch (error) {
        console.error('Error clearing analysis data:', error);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteAccount = async () => {
    try {
      setIsLoading(true);
      
      if (!accessToken) {
        throw new Error('No access token available');
      }
      
      // Call backend to delete account and all data
      await authService.deleteAccount(accessToken);
      
      // Clear all local data
      await clearAuthData();
      const { storageService } = await import('../utils/storage');
      await storageService.clear();
      
      console.log('✅ Account deleted successfully - all data cleared');
    } catch (error) {
      console.error('Delete account error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updateUser = async (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      await saveUserToStorage(updatedUser);
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isGuest,
    accessToken,
    refreshToken,
    login,
    register,
    loginWithGoogle,
    loginWithApple,
    loginAsGuest,
    logout,
    deleteAccount,
    updateUser,
    refreshAccessToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

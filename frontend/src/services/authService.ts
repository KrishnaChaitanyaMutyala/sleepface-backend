import { User } from '../types';

const API_BASE_URL = 'http://192.168.0.165:8000'; // Updated for mobile device access

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  display_name: string;
  agree_to_terms: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface UserProfile {
  user_id: string;
  email: string;
  display_name: string;
  is_premium: boolean;
  streak_count: number;
  created_at: string;
  last_active: string;
  profile_picture_url?: string;
}

class AuthService {
  private async makeRequest<T>(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' = 'GET',
    body?: any,
    token?: string
  ): Promise<T> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      console.log(`🌐 Making ${method} request to: ${url}`);
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const options: RequestInit = {
        method,
        headers,
      };

      if (body) {
        options.body = JSON.stringify(body);
      }

      console.log('🚀 Sending request with options:', {
        method: options.method,
        headers: options.headers,
        hasBody: !!options.body
      });

      const response = await fetch(url, options);
      
      console.log(`📡 Response received: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.log('❌ Error response body:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ Response parsed successfully:', result);
      return result;
    } catch (error) {
      console.error(`💥 API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async register(registerData: RegisterData): Promise<AuthResponse> {
    try {
      console.log('📝 Registering new user...');
      const response = await this.makeRequest<AuthResponse>('/auth/register', 'POST', registerData);
      console.log('✅ User registered successfully');
      return response;
    } catch (error) {
      console.error('❌ Registration failed:', error);
      throw error;
    }
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      console.log('🔐 Logging in user...');
      const response = await this.makeRequest<AuthResponse>('/auth/login', 'POST', credentials);
      console.log('✅ User logged in successfully');
      return response;
    } catch (error) {
      console.error('❌ Login failed:', error);
      throw error;
    }
  }

  async getCurrentUser(token: string): Promise<UserProfile> {
    try {
      console.log('👤 Getting current user profile...');
      const response = await this.makeRequest<UserProfile>('/auth/me', 'GET', undefined, token);
      console.log('✅ User profile retrieved successfully');
      return response;
    } catch (error) {
      console.error('❌ Failed to get user profile:', error);
      throw error;
    }
  }

  async updateProfile(token: string, updateData: Partial<UserProfile>): Promise<UserProfile> {
    try {
      console.log('✏️ Updating user profile...');
      const response = await this.makeRequest<UserProfile>('/auth/profile', 'PUT', updateData, token);
      console.log('✅ User profile updated successfully');
      return response;
    } catch (error) {
      console.error('❌ Failed to update user profile:', error);
      throw error;
    }
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    try {
      console.log('🔄 Refreshing access token...');
      const response = await this.makeRequest<AuthResponse>('/auth/refresh', 'POST', { refresh_token: refreshToken });
      console.log('✅ Access token refreshed successfully');
      return response;
    } catch (error) {
      console.error('❌ Failed to refresh token:', error);
      throw error;
    }
  }

  async logout(token: string, refreshToken: string): Promise<void> {
    try {
      console.log('🚪 Logging out user...');
      await this.makeRequest('/auth/logout', 'POST', { refresh_token: refreshToken }, token);
      console.log('✅ User logged out successfully');
    } catch (error) {
      console.error('❌ Logout failed:', error);
      throw error;
    }
  }

  // Helper method to check if token is expired
  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch (error) {
      console.error('Error checking token expiration:', error);
      return true; // Assume expired if we can't parse
    }
  }

  // Helper method to extract user ID from token
  getUserIdFromToken(token: string): string | null {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.user_id || payload.uid || null;
    } catch (error) {
      console.error('Error extracting user ID from token:', error);
      return null;
    }
  }

  // Delete user account permanently
  async deleteAccount(token: string): Promise<{ success: boolean; message: string }> {
    try {
      console.log('🗑️ Requesting account deletion...');
      const response = await this.makeRequest<{ success: boolean; message: string; user_id: string }>(
        '/auth/delete-account',
        'DELETE',
        null,
        {
          'Authorization': `Bearer ${token}`
        }
      );
      console.log('✅ Account deleted successfully');
      return response;
    } catch (error) {
      console.error('❌ Error deleting account:', error);
      throw error;
    }
  }
}

export const authService = new AuthService();



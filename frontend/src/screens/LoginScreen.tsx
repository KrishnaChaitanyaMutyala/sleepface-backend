import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
  Animated,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';
import CustomIcon from '../components/CustomIcon';
import { Colors, Typography, getThemeColors } from '../design/DesignSystem';
import { useTheme } from '../contexts/ThemeContext';

// ============================================================================
// ANIMATED INPUT FIELD
// ============================================================================
const AnimatedInput: React.FC<{
  icon: string;
  placeholder: string;
  value: string;
  onChangeText: (text: string) => void;
  secureTextEntry?: boolean;
  keyboardType?: any;
  autoCapitalize?: any;
  showPasswordToggle?: boolean;
  onTogglePassword?: () => void;
}> = ({
  icon,
  placeholder,
  value,
  onChangeText,
  secureTextEntry,
  keyboardType,
  autoCapitalize,
  showPasswordToggle,
  onTogglePassword,
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const focusAnim = React.useRef(new Animated.Value(0)).current;

  const handleFocus = () => {
    setIsFocused(true);
    Animated.spring(focusAnim, {
      toValue: 1,
      useNativeDriver: false,
      tension: 50,
      friction: 7,
    }).start();
  };

  const handleBlur = () => {
    setIsFocused(false);
    Animated.spring(focusAnim, {
      toValue: 0,
      useNativeDriver: false,
      tension: 50,
      friction: 7,
    }).start();
  };

  const borderColor = focusAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['rgba(255,255,255,0.2)', Colors.primary],
  });

  return (
    <Animated.View
      style={[
        styles.inputContainer,
        { borderColor, borderWidth: 2 },
      ]}
    >
      <View style={[styles.inputIcon, isFocused && { backgroundColor: Colors.primary + '15' }]}>
        <CustomIcon name={icon} size={20} color={isFocused ? Colors.primary : '#9CA3AF'} />
      </View>
      <TextInput
        style={styles.input}
        placeholder={placeholder}
        placeholderTextColor="#6B7280"
        value={value}
        onChangeText={onChangeText}
        onFocus={handleFocus}
        onBlur={handleBlur}
        secureTextEntry={secureTextEntry}
        keyboardType={keyboardType}
        autoCapitalize={autoCapitalize}
        autoCorrect={false}
      />
      {showPasswordToggle && (
        <TouchableOpacity style={styles.eyeButton} onPress={onTogglePassword}>
          <CustomIcon
            name={secureTextEntry ? 'eye-off' : 'eye'}
            size={20}
            color="#9CA3AF"
          />
        </TouchableOpacity>
      )}
    </Animated.View>
  );
};

// ============================================================================
// MAIN LOGIN SCREEN
// ============================================================================
const LoginScreen: React.FC = () => {
  const navigation = useNavigation();
  const { login, loginAsGuest, isLoading } = useAuth();
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const slideAnim = React.useRef(new Animated.Value(50)).current;

  React.useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.spring(slideAnim, {
        toValue: 0,
        useNativeDriver: true,
        tension: 50,
        friction: 7,
      }),
    ]).start();
  }, []);

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Missing Information', 'Please fill in all fields');
      return;
    }

    if (!isValidEmail(email)) {
      Alert.alert('Invalid Email', 'Please enter a valid email address');
      return;
    }

    try {
      await login(email, password);
      // Navigate to Home instead of goBack to avoid navigation errors
      navigation.reset({
        index: 0,
        routes: [{ name: 'Home' as never }],
      });
    } catch (error: any) {
      Alert.alert('Login Failed', error?.message || 'Please check your credentials and try again.');
    }
  };

  const handleGuestLogin = async () => {
    try {
      await loginAsGuest();
      // Guest login will automatically navigate to MainTabs
      // Camera welcome modal will appear automatically for first-time guests
    } catch (error: any) {
      Alert.alert('Error', error?.message || 'Failed to continue as guest. Please try again.');
    }
  };

  const handleForgotPassword = () => {
    Alert.alert('Forgot Password', 'Password reset functionality coming soon!');
  };

  return (
    <LinearGradient
      colors={[colors.background, colors.surfaceSecondary, colors.background]}
      style={styles.container}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <Animated.View
            style={[
              styles.content,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            {/* Logo Section */}
            <View style={styles.logoSection}>
              <View style={styles.logoContainer}>
                <LinearGradient
                  colors={[Colors.primary, Colors.accent]}
                  style={styles.logoGradient}
                >
                  <CustomIcon name="zap" size={40} color="#FFFFFF" />
                </LinearGradient>
              </View>
              
              <Text style={styles.appName}>HappyFace</Text>
              <Text style={styles.tagline}>Track your wellness journey</Text>
            </View>

            {/* Welcome Back */}
            <View style={styles.welcomeSection}>
              <Text style={styles.welcomeTitle}>Welcome Back</Text>
              <Text style={styles.welcomeSubtitle}>
                Sign in to continue your skin and sleep tracking
              </Text>
            </View>

            {/* Form */}
            <View style={styles.formSection}>
              <AnimatedInput
                icon="mail"
                placeholder="Email address"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />

              <AnimatedInput
                icon="lock"
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                showPasswordToggle
                onTogglePassword={() => setShowPassword(!showPassword)}
                autoCapitalize="none"
              />

              <TouchableOpacity
                style={styles.forgotButton}
                onPress={handleForgotPassword}
              >
                <Text style={styles.forgotText}>Forgot password?</Text>
              </TouchableOpacity>

              {/* Login Button */}
              <TouchableOpacity
                style={styles.loginButton}
                onPress={handleLogin}
                disabled={isLoading}
                activeOpacity={0.9}
              >
                <LinearGradient
                  colors={[Colors.primary, Colors.accent]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={styles.loginGradient}
                >
                  {isLoading ? (
                    <Text style={styles.loginButtonText}>Signing in...</Text>
                  ) : (
                    <>
                      <CustomIcon name="log-in" size={20} color="#FFFFFF" />
                      <Text style={styles.loginButtonText}>Sign In</Text>
                    </>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            </View>

            {/* Divider */}
            <View style={styles.dividerSection}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>or continue with</Text>
              <View style={styles.dividerLine} />
            </View>

            {/* Social Buttons */}
            <View style={styles.socialSection}>
              <TouchableOpacity style={styles.socialButton}>
                <View style={[styles.socialIcon, { backgroundColor: '#DB4437' }]}>
                  <CustomIcon name="logo-google" size={20} color="#FFFFFF" />
                </View>
                <Text style={styles.socialText}>Google</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.socialButton}>
                <View style={[styles.socialIcon, { backgroundColor: '#000000' }]}>
                  <CustomIcon name="logo-apple" size={20} color="#FFFFFF" />
                </View>
                <Text style={styles.socialText}>Apple</Text>
              </TouchableOpacity>
            </View>

            {/* Guest Login */}
            <TouchableOpacity
              style={styles.guestButton}
              onPress={handleGuestLogin}
              disabled={isLoading}
            >
              <CustomIcon name="user" size={18} color="#9CA3AF" />
              <Text style={styles.guestText}>
                {isLoading ? 'Loading...' : 'Continue as Guest'}
              </Text>
            </TouchableOpacity>

            {/* Footer */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>Don't have an account? </Text>
              <TouchableOpacity onPress={() => navigation.navigate('Register' as never)}>
                <Text style={styles.footerLink}>Sign Up</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
};

// ============================================================================
// STYLES
// ============================================================================
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingTop: 60,
    paddingBottom: 40,
  },
  content: {
    paddingHorizontal: 24,
  },
  
  // Logo Section
  logoSection: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoContainer: {
    marginBottom: 20,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 10,
  },
  logoGradient: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  appName: {
    fontSize: 32,
    fontWeight: '800',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  tagline: {
    fontSize: 15,
    color: '#9CA3AF',
    fontWeight: '500',
  },
  
  // Welcome Section
  welcomeSection: {
    marginBottom: 32,
  },
  welcomeTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  welcomeSubtitle: {
    fontSize: 15,
    color: '#9CA3AF',
    lineHeight: 22,
  },
  
  // Form
  formSection: {
    marginBottom: 24,
    gap: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1F2937',
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  inputIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#374151',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#FFFFFF',
  },
  eyeButton: {
    padding: 8,
  },
  forgotButton: {
    alignSelf: 'flex-end',
    marginTop: -8,
  },
  forgotText: {
    fontSize: 14,
    color: Colors.primary,
    fontWeight: '600',
  },
  
  // Login Button
  loginButton: {
    borderRadius: 16,
    overflow: 'hidden',
    marginTop: 8,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 10,
  },
  loginGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    gap: 10,
  },
  loginButtonText: {
    fontSize: 17,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  
  // Divider
  dividerSection: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 32,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#374151',
  },
  dividerText: {
    fontSize: 13,
    color: '#6B7280',
    paddingHorizontal: 16,
    fontWeight: '500',
  },
  
  // Social
  socialSection: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  socialButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1F2937',
    paddingVertical: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#374151',
    gap: 10,
  },
  socialIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  socialText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#F3F4F6',
  },
  
  // Guest
  guestButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1F2937',
    paddingVertical: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#374151',
    gap: 10,
  },
  guestText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#9CA3AF',
  },
  
  // Footer
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 32,
  },
  footerText: {
    fontSize: 15,
    color: '#9CA3AF',
  },
  footerLink: {
    fontSize: 15,
    color: Colors.primary,
    fontWeight: '700',
  },
});

export default LoginScreen;
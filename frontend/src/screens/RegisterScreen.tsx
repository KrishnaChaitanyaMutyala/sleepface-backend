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
// ANIMATED INPUT FIELD (Reusable)
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
    <Animated.View style={[styles.inputContainer, { borderColor, borderWidth: 2 }]}>
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
// PASSWORD STRENGTH INDICATOR
// ============================================================================
const PasswordStrength: React.FC<{ password: string }> = ({ password }) => {
  const getStrength = () => {
    if (password.length === 0) return { strength: 0, label: '', color: '#374151' };
    if (password.length < 6) return { strength: 1, label: 'Weak', color: '#EF4444' };
    if (password.length < 8) return { strength: 2, label: 'Fair', color: '#F59E0B' };
    if (password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password)) {
      return { strength: 4, label: 'Strong', color: '#10B981' };
    }
    return { strength: 3, label: 'Good', color: '#3B82F6' };
  };

  const { strength, label, color } = getStrength();

  if (password.length === 0) return null;

  return (
    <View style={styles.strengthContainer}>
      <View style={styles.strengthBar}>
        {[1, 2, 3, 4].map((level) => (
          <View
            key={level}
            style={[
              styles.strengthSegment,
              level <= strength && { backgroundColor: color },
            ]}
          />
        ))}
      </View>
      <Text style={[styles.strengthLabel, { color }]}>{label}</Text>
    </View>
  );
};

// ============================================================================
// MAIN REGISTER SCREEN
// ============================================================================
const RegisterScreen: React.FC = () => {
  const navigation = useNavigation();
  const { register, isLoading } = useAuth();
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const [formData, setFormData] = useState({
    displayName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeToTerms, setAgreeToTerms] = useState(false);
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

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleRegister = async () => {
    if (!formData.displayName.trim() || !formData.email.trim() || !formData.password.trim()) {
      Alert.alert('Missing Information', 'Please fill in all fields');
      return;
    }

    if (!isValidEmail(formData.email)) {
      Alert.alert('Invalid Email', 'Please enter a valid email address');
      return;
    }

    if (formData.password.length < 8) {
      Alert.alert('Weak Password', 'Password must be at least 8 characters long');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Password Mismatch', 'Passwords do not match');
      return;
    }

    if (!agreeToTerms) {
      Alert.alert('Terms Required', 'Please agree to the Terms and Conditions');
      return;
    }

    try {
      await register({
        email: formData.email,
        password: formData.password,
        display_name: formData.displayName,
        agree_to_terms: agreeToTerms
      });
      // Navigate to Camera screen for first selfie experience (like guest users)
      navigation.reset({
        index: 0,
        routes: [{ name: 'MainTabs' as never }],
      });
      // Navigate to Camera after a short delay to ensure MainTabs is loaded
      setTimeout(() => {
        navigation.navigate('Camera' as never);
      }, 100);
    } catch (error: any) {
      Alert.alert('Registration Failed', error?.message || 'Please try again later.');
    }
  };

  const handleTermsPress = () => {
    Alert.alert('Terms and Conditions', 'Terms and conditions will be displayed here');
  };

  const passwordsMatch = formData.confirmPassword.length > 0 && formData.password === formData.confirmPassword;
  const passwordsDontMatch = formData.confirmPassword.length > 0 && formData.password !== formData.confirmPassword;

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
            {/* Back Button */}
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => navigation.goBack()}
            >
              <CustomIcon name="chevron-left" size={24} color="#FFFFFF" />
            </TouchableOpacity>

            {/* Logo Section */}
            <View style={styles.logoSection}>
              <View style={styles.logoContainer}>
                <LinearGradient
                  colors={[Colors.primary, Colors.accent]}
                  style={styles.logoGradient}
                >
                  <CustomIcon name="user-plus" size={40} color="#FFFFFF" />
                </LinearGradient>
              </View>
              
              <Text style={styles.appName}>Create Account</Text>
              <Text style={styles.tagline}>Join HappyFace and start your journey</Text>
            </View>

            {/* Form */}
            <View style={styles.formSection}>
              <AnimatedInput
                icon="user"
                placeholder="Full name"
                value={formData.displayName}
                onChangeText={(value) => handleInputChange('displayName', value)}
                autoCapitalize="words"
              />

              <AnimatedInput
                icon="mail"
                placeholder="Email address"
                value={formData.email}
                onChangeText={(value) => handleInputChange('email', value)}
                keyboardType="email-address"
                autoCapitalize="none"
              />

              <View>
                <AnimatedInput
                  icon="lock"
                  placeholder="Password (min 8 characters)"
                  value={formData.password}
                  onChangeText={(value) => handleInputChange('password', value)}
                  secureTextEntry={!showPassword}
                  showPasswordToggle
                  onTogglePassword={() => setShowPassword(!showPassword)}
                  autoCapitalize="none"
                />
                <PasswordStrength password={formData.password} />
              </View>

              <View>
                <AnimatedInput
                  icon="lock"
                  placeholder="Confirm password"
                  value={formData.confirmPassword}
                  onChangeText={(value) => handleInputChange('confirmPassword', value)}
                  secureTextEntry={!showConfirmPassword}
                  showPasswordToggle
                  onTogglePassword={() => setShowConfirmPassword(!showConfirmPassword)}
                  autoCapitalize="none"
                />
                {passwordsDontMatch && (
                  <View style={styles.errorContainer}>
                    <CustomIcon name="alert-circle" size={14} color="#EF4444" />
                    <Text style={styles.errorText}>Passwords do not match</Text>
                  </View>
                )}
                {passwordsMatch && (
                  <View style={styles.successContainer}>
                    <CustomIcon name="check-circle" size={14} color="#10B981" />
                    <Text style={styles.successText}>Passwords match</Text>
                  </View>
                )}
              </View>

              {/* Terms Checkbox */}
              <TouchableOpacity
                style={styles.termsContainer}
                onPress={() => setAgreeToTerms(!agreeToTerms)}
                activeOpacity={0.8}
              >
                <View style={[styles.checkbox, agreeToTerms && styles.checkboxActive]}>
                  {agreeToTerms && (
                    <CustomIcon name="check" size={14} color="#FFFFFF" />
                  )}
                </View>
                <Text style={styles.termsText}>
                  I agree to the{' '}
                  <Text style={styles.termsLink} onPress={handleTermsPress}>
                    Terms and Conditions
                  </Text>
                </Text>
              </TouchableOpacity>

              {/* Register Button */}
              <TouchableOpacity
                style={styles.registerButton}
                onPress={handleRegister}
                disabled={isLoading}
                activeOpacity={0.9}
              >
                <LinearGradient
                  colors={[Colors.primary, Colors.accent]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={styles.registerGradient}
                >
                  {isLoading ? (
                    <Text style={styles.registerButtonText}>Creating account...</Text>
                  ) : (
                    <>
                      <CustomIcon name="user-plus" size={20} color="#FFFFFF" />
                      <Text style={styles.registerButtonText}>Create Account</Text>
                    </>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            </View>

            {/* Divider */}
            <View style={styles.dividerSection}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>or sign up with</Text>
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

            {/* Footer */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>Already have an account? </Text>
              <TouchableOpacity onPress={() => navigation.navigate('Login' as never)}>
                <Text style={styles.footerLink}>Sign In</Text>
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
  
  // Back Button
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#1F2937',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  
  // Logo Section
  logoSection: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logoContainer: {
    marginBottom: 16,
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
    fontSize: 28,
    fontWeight: '800',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  tagline: {
    fontSize: 15,
    color: '#9CA3AF',
    textAlign: 'center',
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
  
  // Password Strength
  strengthContainer: {
    marginTop: 12,
    gap: 8,
  },
  strengthBar: {
    flexDirection: 'row',
    gap: 4,
    height: 4,
  },
  strengthSegment: {
    flex: 1,
    backgroundColor: '#374151',
    borderRadius: 2,
  },
  strengthLabel: {
    fontSize: 12,
    fontWeight: '600',
  },
  
  // Error/Success Messages
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 8,
  },
  errorText: {
    fontSize: 12,
    color: '#EF4444',
    fontWeight: '500',
  },
  successContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 8,
  },
  successText: {
    fontSize: 12,
    color: '#10B981',
    fontWeight: '500',
  },
  
  // Terms
  termsContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginTop: 4,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#374151',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  termsText: {
    flex: 1,
    fontSize: 14,
    color: '#9CA3AF',
    lineHeight: 20,
  },
  termsLink: {
    color: Colors.primary,
    fontWeight: '600',
  },
  
  // Register Button
  registerButton: {
    borderRadius: 16,
    overflow: 'hidden',
    marginTop: 8,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 10,
  },
  registerGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    gap: 10,
  },
  registerButtonText: {
    fontSize: 17,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  
  // Divider
  dividerSection: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 24,
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
    marginBottom: 24,
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
  
  // Footer
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
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

export default RegisterScreen;
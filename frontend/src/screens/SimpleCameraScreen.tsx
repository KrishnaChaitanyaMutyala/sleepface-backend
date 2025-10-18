import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  StatusBar,
  TextInput,
  ScrollView,
  Modal,
  Dimensions,
  Animated,
  PanResponder,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { useAnalysis } from '../contexts/AnalysisContext';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { RoutineData } from '../types';
import SkincareMultiSelect from '../components/SkincareMultiSelect';
import CustomIcon from '../components/CustomIcon';
import { Colors, Typography, Spacing, BorderRadius, Shadows, getThemeColors, ButtonStyles } from '../design/DesignSystem';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width: screenWidth } = Dimensions.get('window');

// ============================================================================
// ULTRA SMOOTH SLIDER - Fixed shaking issue
// ============================================================================
const SmoothSlider: React.FC<{
  value: number;
  onValueChange: (value: number) => void;
  min: number;
  max: number;
  step: number;
  label: string;
  unit: string;
  color: string;
  icon: string;
  colors: any;
}> = ({ value, onValueChange, min, max, step, label, unit, color, icon, colors }) => {
  const [isDragging, setIsDragging] = useState(false);
  const sliderWidth = screenWidth - 80;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  
  // Calculate thumb position
  const getThumbPosition = (val: number) => {
    const percentage = ((val - min) / (max - min)) * 100;
    return (percentage / 100) * (sliderWidth - 40);
  };

  const [thumbPosition, setThumbPosition] = useState(getThumbPosition(value));

  // Create pan responder for smooth dragging
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: () => true,
      onPanResponderGrant: () => {
        setIsDragging(true);
        Animated.spring(scaleAnim, {
          toValue: 1.2,
          useNativeDriver: true,
          tension: 150,
          friction: 7,
        }).start();
      },
      onPanResponderMove: (_, gestureState) => {
        // Calculate new position
        const newPosition = Math.max(
          0,
          Math.min(sliderWidth - 40, thumbPosition + gestureState.dx)
        );
        
        // Calculate new value
        const newPercentage = (newPosition / (sliderWidth - 40)) * 100;
        const rawValue = min + (newPercentage / 100) * (max - min);
        const steppedValue = Math.round(rawValue / step) * step;
        const clampedValue = Math.max(min, Math.min(max, steppedValue));
        
        // Update value immediately
        onValueChange(clampedValue);
      },
      onPanResponderRelease: () => {
        setIsDragging(false);
        Animated.spring(scaleAnim, {
          toValue: 1,
          useNativeDriver: true,
          tension: 150,
          friction: 7,
        }).start();
        
        // Update thumb position to final value
        setThumbPosition(getThumbPosition(value));
      },
      onPanResponderTerminate: () => {
        setIsDragging(false);
        Animated.spring(scaleAnim, {
          toValue: 1,
          useNativeDriver: true,
        }).start();
      },
    })
  ).current;

  // Update thumb position when value changes externally
  React.useEffect(() => {
    if (!isDragging) {
      setThumbPosition(getThumbPosition(value));
    }
  }, [value, isDragging]);

  // Handle track press
  const handleTrackPress = (event: any) => {
    const { locationX } = event.nativeEvent;
    const newPercentage = Math.max(0, Math.min(100, (locationX / sliderWidth) * 100));
    const rawValue = min + (newPercentage / 100) * (max - min);
    const steppedValue = Math.round(rawValue / step) * step;
    const clampedValue = Math.max(min, Math.min(max, steppedValue));
    
    onValueChange(clampedValue);
    setThumbPosition(getThumbPosition(clampedValue));
  };

  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <View style={styles.sliderContainer}>
      {/* Header with Icon */}
      <View style={styles.sliderHeader}>
        <View style={styles.sliderLabelRow}>
          <View style={[styles.iconContainer, { backgroundColor: color + '15' }]}>
            <CustomIcon name={icon} size={20} color={color} />
          </View>
          <Text style={[styles.labelText, { color: colors.textPrimary }]}>
            {label}
          </Text>
        </View>
        
        {/* Value Display */}
        <View style={[styles.valueChip, { backgroundColor: color + '15', borderColor: color + '30' }]}>
          <Text style={[styles.valueNumber, { color }]}>
            {value.toFixed(step < 1 ? 1 : 0)}
          </Text>
          <Text style={[styles.valueUnit, { color: color + 'DD' }]}>{unit}</Text>
        </View>
      </View>

      {/* Slider Track */}
      <View style={styles.trackContainer}>
        <TouchableOpacity
          activeOpacity={1}
          onPress={handleTrackPress}
          style={styles.trackWrapper}
        >
          {/* Background Track */}
          <View style={[styles.track, { backgroundColor: colors.surfaceSecondary }]}>
            {/* Filled Track with Gradient */}
            <LinearGradient
              colors={[color, color + 'DD']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={[styles.trackFill, { width: `${percentage}%` }]}
            />
          </View>
        </TouchableOpacity>

        {/* Draggable Thumb */}
        <Animated.View
          {...panResponder.panHandlers}
          style={[
            styles.thumb,
            {
              left: thumbPosition,
              backgroundColor: color,
              transform: [{ scale: scaleAnim }],
              shadowColor: color,
              shadowOpacity: isDragging ? 0.5 : 0.3,
              shadowRadius: isDragging ? 16 : 10,
              elevation: isDragging ? 12 : 8,
            },
          ]}
        >
          <View style={styles.thumbInner}>
            <View style={[styles.thumbDot, { backgroundColor: '#FFFFFF' }]} />
          </View>
        </Animated.View>
      </View>

      {/* Min/Max Labels */}
      <View style={styles.rangeLabels}>
        <Text style={[styles.rangeLabel, { color: colors.textTertiary }]}>
          {min}{unit}
        </Text>
        <View style={styles.rangeDivider} />
        <Text style={[styles.rangeLabel, { color: colors.textTertiary }]}>
          {max}{unit}
        </Text>
      </View>
    </View>
  );
};

// ============================================================================
// GUEST WELCOME MODAL (for guest users only)
// ============================================================================
const GuestWelcomeModal: React.FC<{
  visible: boolean;
  onClose: () => void;
}> = ({ visible, onClose }) => {
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const scaleAnim = useRef(new Animated.Value(0.8)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.spring(scaleAnim, {
          toValue: 1,
          useNativeDriver: true,
          tension: 50,
          friction: 7,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      scaleAnim.setValue(0.8);
      opacityAnim.setValue(0);
    }
  }, [visible]);

  return (
    <Modal transparent visible={visible} animationType="fade">
      <View style={styles.welcomeModalOverlay}>
        <Animated.View
          style={[
            styles.welcomeModalContent,
            { 
              backgroundColor: colors.surface,
              transform: [{ scale: scaleAnim }],
              opacity: opacityAnim,
            },
          ]}
        >
          {/* Close Button */}
          <TouchableOpacity style={styles.welcomeCloseButton} onPress={onClose}>
            <CustomIcon name="close" size={24} color={colors.textSecondary} />
          </TouchableOpacity>

          {/* Gradient Header */}
          <LinearGradient
            colors={[Colors.primary, Colors.accent]}
            style={styles.welcomeModalHeader}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          >
            <View style={styles.welcomeIconContainer}>
              <CustomIcon name="sparkles" size={48} color="#FFFFFF" />
            </View>
          </LinearGradient>

          {/* Content */}
          <View style={styles.welcomeModalBody}>
            <Text style={[styles.welcomeTitle, { color: colors.textPrimary }]}>
              Welcome to SleepFace! 👋
            </Text>
            
            <Text style={[styles.welcomeMessage, { color: colors.textSecondary }]}>
              Track your sleep quality and skin health with AI-powered analysis. Get personalized insights and watch your wellness journey unfold.
            </Text>

            <View style={styles.welcomeFeatures}>
              <View style={styles.welcomeFeature}>
                <View style={[styles.welcomeFeatureIcon, { backgroundColor: Colors.primary + '15' }]}>
                  <CustomIcon name="camera" size={20} color={Colors.primary} />
                </View>
                <Text style={[styles.welcomeFeatureText, { color: colors.textSecondary }]}>
                  Daily selfie analysis
                </Text>
              </View>

              <View style={styles.welcomeFeature}>
                <View style={[styles.welcomeFeatureIcon, { backgroundColor: Colors.accent + '15' }]}>
                  <CustomIcon name="trending-up" size={20} color={Colors.accent} />
                </View>
                <Text style={[styles.welcomeFeatureText, { color: colors.textSecondary }]}>
                  Track your progress
                </Text>
              </View>

              <View style={styles.welcomeFeature}>
                <View style={[styles.welcomeFeatureIcon, { backgroundColor: Colors.success + '15' }]}>
                  <CustomIcon name="lightbulb" size={20} color={Colors.success} />
                </View>
                <Text style={[styles.welcomeFeatureText, { color: colors.textSecondary }]}>
                  Personalized tips
                </Text>
              </View>
            </View>

            <Text style={[styles.welcomeNote, { color: colors.textTertiary }]}>
              You're browsing as a guest. Sign up to save your data and unlock all features!
            </Text>

            {/* Action Button */}
            <TouchableOpacity style={styles.welcomeActionButton} onPress={onClose}>
              <LinearGradient
                colors={[Colors.primary, Colors.accent]}
                style={styles.welcomeActionGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
              >
                <CustomIcon name="camera" size={20} color="#FFFFFF" />
                <Text style={styles.welcomeActionText}>Take Your First Selfie</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </View>
    </Modal>
  );
};

// ============================================================================
// REGISTERED USER WELCOME MODAL (for new registered users only - shows once)
// ============================================================================
const RegisteredWelcomeModal: React.FC<{
  visible: boolean;
  onClose: () => void;
}> = ({ visible, onClose }) => {
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const scaleAnim = useRef(new Animated.Value(0.8)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.spring(scaleAnim, {
          toValue: 1,
          useNativeDriver: true,
          tension: 50,
          friction: 7,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      scaleAnim.setValue(0.8);
      opacityAnim.setValue(0);
    }
  }, [visible]);

  return (
    <Modal transparent visible={visible} animationType="fade">
      <View style={styles.welcomeModalOverlay}>
        <Animated.View
          style={[
            styles.welcomeModalContent,
            { 
              backgroundColor: colors.surface,
              transform: [{ scale: scaleAnim }],
              opacity: opacityAnim,
            },
          ]}
        >
          {/* Close Button */}
          <TouchableOpacity style={styles.welcomeCloseButton} onPress={onClose}>
            <CustomIcon name="close" size={24} color={colors.textSecondary} />
          </TouchableOpacity>

          {/* Gradient Header */}
          <LinearGradient
            colors={[Colors.success, Colors.primary]}
            style={styles.welcomeModalHeader}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          >
            <View style={styles.welcomeIconContainer}>
              <CustomIcon name="checkmark-circle" size={56} color="#FFFFFF" />
            </View>
          </LinearGradient>

          {/* Content */}
          <View style={styles.welcomeModalBody}>
            <Text style={[styles.welcomeTitle, { color: colors.textPrimary }]}>
              Welcome Aboard! 🎉
            </Text>
            
            <Text style={[styles.welcomeMessage, { color: colors.textSecondary }]}>
              Thank you for joining SleepFace! Your account is ready and your data will be securely saved. Let's start your wellness journey with your first selfie!
            </Text>

            <View style={styles.welcomeFeatures}>
              <View style={styles.welcomeFeature}>
                <View style={[styles.welcomeFeatureIcon, { backgroundColor: Colors.success + '15' }]}>
                  <CustomIcon name="save" size={20} color={Colors.success} />
                </View>
                <Text style={[styles.welcomeFeatureText, { color: colors.textSecondary }]}>
                  Your data is saved forever
                </Text>
              </View>

              <View style={styles.welcomeFeature}>
                <View style={[styles.welcomeFeatureIcon, { backgroundColor: Colors.primary + '15' }]}>
                  <CustomIcon name="trending-up" size={20} color={Colors.primary} />
                </View>
                <Text style={[styles.welcomeFeatureText, { color: colors.textSecondary }]}>
                  Track long-term progress
                </Text>
              </View>

              <View style={styles.welcomeFeature}>
                <View style={[styles.welcomeFeatureIcon, { backgroundColor: Colors.accent + '15' }]}>
                  <CustomIcon name="star" size={20} color={Colors.accent} />
                </View>
                <Text style={[styles.welcomeFeatureText, { color: colors.textSecondary }]}>
                  Unlock all premium features
                </Text>
              </View>
            </View>

            <Text style={[styles.welcomeNote, { color: colors.textTertiary }]}>
              Your wellness journey starts now. Take your first selfie to get personalized insights!
            </Text>

            {/* Action Button */}
            <TouchableOpacity style={styles.welcomeActionButton} onPress={onClose}>
              <LinearGradient
                colors={[Colors.success, Colors.primary]}
                style={styles.welcomeActionGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
              >
                <CustomIcon name="camera" size={20} color="#FFFFFF" />
                <Text style={styles.welcomeActionText}>Take My First Selfie</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </View>
    </Modal>
  );
};

// ============================================================================
// MAIN CAMERA SCREEN COMPONENT
// ============================================================================
const SimpleCameraScreen: React.FC = () => {
  const navigation = useNavigation();
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const { isGuest } = useAuth();
  const { analyzeImage, isLoading } = useAnalysis();
  const [isCapturing, setIsCapturing] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [showRoutineModal, setShowRoutineModal] = useState(false);
  const [showGuestWelcome, setShowGuestWelcome] = useState(false);
  const [showRegisteredWelcome, setShowRegisteredWelcome] = useState(false);
  const [routineData, setRoutineData] = useState<RoutineData>({
    sleep_hours: 7.5,
    water_intake: 8,
    product_used: undefined,
    skincare_products: [],
    daily_note: undefined,
  });

  // Check if guest user should see welcome modal
  useEffect(() => {
    const checkGuestWelcome = async () => {
      if (isGuest) {
        const hasSeenGuestWelcome = await AsyncStorage.getItem('hasSeenGuestWelcome');
        if (!hasSeenGuestWelcome) {
          setShowGuestWelcome(true);
        }
      }
    };
    checkGuestWelcome();
  }, [isGuest]);

  // Check if registered user should see welcome modal (only once after registration)
  useEffect(() => {
    const checkRegisteredWelcome = async () => {
      if (!isGuest) {
        const hasSeenRegisteredWelcome = await AsyncStorage.getItem('hasSeenRegisteredWelcome');
        if (!hasSeenRegisteredWelcome) {
          setShowRegisteredWelcome(true);
        }
      }
    };
    checkRegisteredWelcome();
  }, [isGuest]);

  const takePicture = async () => {
    if (isCapturing) return;

    try {
      setIsCapturing(true);
      const cameraPermission = await ImagePicker.requestCameraPermissionsAsync();
      
      if (!cameraPermission.granted) {
        Alert.alert(
          'Camera Permission Required',
          'Please enable camera access in your device settings.',
          [{ text: 'OK' }]
        );
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
        cameraType: ImagePicker.CameraType.front, // Always front camera for selfies
      });

      if (!result.canceled && result.assets[0]?.uri) {
        setSelectedImage(result.assets[0].uri);
        setShowRoutineModal(true);
      }
    } catch (error) {
      console.error('Error taking picture:', error);
      Alert.alert('Error', 'Failed to take picture. Please try again.');
    } finally {
      setIsCapturing(false);
    }
  };

  const pickFromGallery = async () => {
    try {
      const mediaPermission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (!mediaPermission.granted) {
        Alert.alert(
          'Media Library Permission Required',
          'Please enable photo library access in your device settings.',
          [{ text: 'OK' }]
        );
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]?.uri) {
        setSelectedImage(result.assets[0].uri);
        setShowRoutineModal(true);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to pick image. Please try again.');
    }
  };

  const handleAnalyzeImage = async () => {
    if (!selectedImage) return;
    
    try {
      setIsCapturing(true);
      await analyzeImage(selectedImage, routineData);
      setShowRoutineModal(false);
      setRoutineData({
        sleep_hours: 7.5,
        water_intake: 8,
        product_used: undefined,
        skincare_products: [],
        daily_note: undefined,
      });
      navigation.navigate('Analysis' as never);
    } catch (error) {
      console.error('Error analyzing image:', error);
      Alert.alert('Error', 'Failed to analyze image. Please try again.');
    } finally {
      setIsCapturing(false);
    }
  };

  const handleSkipRoutine = () => {
    setRoutineData({
      sleep_hours: undefined,
      water_intake: undefined,
      product_used: undefined,
      skincare_products: [],
      daily_note: undefined,
    });
    handleAnalyzeImage();
  };

  const handleCloseModal = () => {
    setShowRoutineModal(false);
    setRoutineData({
      sleep_hours: 7.5,
      water_intake: 8,
      product_used: undefined,
      skincare_products: [],
      daily_note: undefined,
    });
  };

  const handleGuestWelcomeClose = async () => {
    setShowGuestWelcome(false);
    await AsyncStorage.setItem('hasSeenGuestWelcome', 'true');
  };

  const handleRegisteredWelcomeClose = async () => {
    setShowRegisteredWelcome(false);
    await AsyncStorage.setItem('hasSeenRegisteredWelcome', 'true');
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <StatusBar barStyle={isDark ? "light-content" : "dark-content"} />
      
      {/* Guest Welcome Modal */}
      <GuestWelcomeModal
        visible={showGuestWelcome}
        onClose={handleGuestWelcomeClose}
      />

      {/* Registered User Welcome Modal */}
      <RegisteredWelcomeModal
        visible={showRegisteredWelcome}
        onClose={handleRegisteredWelcomeClose}
      />
      
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Modern Header */}
        <View style={styles.modernHeader}>
          <TouchableOpacity 
            style={[styles.backButton, { backgroundColor: colors.surfaceSecondary }]} 
            onPress={() => navigation.goBack()}
          >
            <CustomIcon name="chevronLeft" size={24} color={colors.textPrimary} />
          </TouchableOpacity>
          
          <Text style={[styles.modernTitle, { color: colors.textPrimary }]}>
            Take Selfie
          </Text>
          
          <View style={styles.headerSpacer} />
        </View>

        {/* Hero Section */}
        <View style={styles.heroSection}>
          <LinearGradient
            colors={[Colors.primary + '20', Colors.accent + '20']}
            style={styles.heroGradient}
          >
            <View style={styles.cameraHero}>
              <CustomIcon name="camera" size={64} color={Colors.primary} />
            </View>
          </LinearGradient>
          
          <Text style={[styles.heroTitle, { color: colors.textPrimary }]}>
            Capture Your Skin Journey
          </Text>
          <Text style={[styles.heroSubtitle, { color: colors.textSecondary }]}>
            Take a clear selfie for AI-powered skin analysis
          </Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionGrid}>
          <TouchableOpacity
            style={styles.primaryActionButton}
            onPress={takePicture}
            disabled={isCapturing}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={[Colors.primary, Colors.accent]}
              style={styles.buttonGradient}
            >
              {isCapturing ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <>
                  <CustomIcon name="camera" size={28} color="#FFFFFF" />
                  <Text style={styles.primaryButtonText}>Take Selfie</Text>
                </>
              )}
            </LinearGradient>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.secondaryActionButton, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}
            onPress={pickFromGallery}
            activeOpacity={0.8}
          >
            <CustomIcon name="image" size={24} color={Colors.primary} />
            <Text style={[styles.secondaryButtonText, { color: colors.textPrimary }]}>
              Choose from Gallery
            </Text>
          </TouchableOpacity>
        </View>

        {/* Tips Card */}
        <View style={[styles.tipsCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={styles.tipsHeader}>
            <View style={[styles.tipsIcon, { backgroundColor: Colors.accent + '15' }]}>
              <CustomIcon name="lightbulb" size={20} color={Colors.accent} />
            </View>
            <Text style={[styles.tipsTitle, { color: colors.textPrimary }]}>
              Pro Tips
            </Text>
          </View>
          
          <View style={styles.tipsList}>
            {[
              'Use natural daylight or bright lighting',
              'Look directly at the camera',
              'Keep your face centered in frame',
              'Remove glasses and pull back hair',
            ].map((tip, index) => (
              <View key={index} style={styles.tipRow}>
                <View style={[styles.tipBullet, { backgroundColor: Colors.primary + '30' }]}>
                  <Text style={[styles.tipBulletText, { color: Colors.primary }]}>
                    {index + 1}
                  </Text>
                </View>
                <Text style={[styles.tipText, { color: colors.textSecondary }]}>
                  {tip}
                </Text>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* Routine Modal */}
      <Modal
        visible={showRoutineModal}
        animationType="slide"
        transparent={true}
        onRequestClose={handleCloseModal}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.premiumModal, { backgroundColor: colors.background }]}>
            <View style={[styles.modalHandle, { backgroundColor: colors.textTertiary }]} />
            
            <View style={styles.premiumModalHeader}>
              <View>
                <Text style={[styles.modalMainTitle, { color: colors.textPrimary }]}>
                  Daily Routine
                </Text>
                <Text style={[styles.modalMainSubtitle, { color: colors.textSecondary }]}>
                  Help us personalize your insights
                </Text>
              </View>
              
              <TouchableOpacity
                style={[styles.closeButton, { backgroundColor: colors.surfaceSecondary }]}
                onPress={handleCloseModal}
              >
                <CustomIcon name="close" size={20} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <ScrollView 
              style={styles.modalScroll}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.modalScrollContent}
            >
              {/* Sleep Slider */}
              <SmoothSlider
                value={routineData.sleep_hours || 7.5}
                onValueChange={(value) => setRoutineData(prev => ({
                  ...prev,
                  sleep_hours: value
                }))}
                min={0}
                max={12}
                step={0.5}
                label="Sleep Duration"
                unit="h"
                color="#5B8DEF"
                icon="moon"
                colors={colors}
              />

              {/* Water Slider */}
              <SmoothSlider
                value={routineData.water_intake || 8}
                onValueChange={(value) => setRoutineData(prev => ({
                  ...prev,
                  water_intake: value
                }))}
                min={0}
                max={20}
                step={1}
                label="Water Intake"
                unit=" glasses"
                color="#4ECDC4"
                icon="droplet"
                colors={colors}
              />

              {/* Skincare Products */}
              <View style={[styles.inputSection, { backgroundColor: colors.surface, borderColor: colors.border }]}>
                <View style={styles.inputHeader}>
                  <View style={[styles.inputIcon, { backgroundColor: Colors.primary + '15' }]}>
                    <CustomIcon name="sparkles" size={18} color={Colors.primary} />
                  </View>
                  <Text style={[styles.inputTitle, { color: colors.textPrimary }]}>
                    Skincare Products
                  </Text>
                </View>
                <SkincareMultiSelect
                  selectedProducts={routineData.skincare_products || []}
                  onSelectionChange={(products) => setRoutineData(prev => ({
                    ...prev,
                    skincare_products: products,
                    product_used: products.length > 0 ? products.join(', ') : undefined
                  }))}
                  placeholder="Select products you used today..."
                />
              </View>

              {/* Daily Note */}
              <View style={[styles.inputSection, { backgroundColor: colors.surface, borderColor: colors.border }]}>
                <View style={styles.inputHeader}>
                  <View style={[styles.inputIcon, { backgroundColor: Colors.accent + '15' }]}>
                    <CustomIcon name="edit" size={18} color={Colors.accent} />
                  </View>
                  <Text style={[styles.inputTitle, { color: colors.textPrimary }]}>
                    Daily Note (Optional)
                  </Text>
                </View>
                <TextInput
                  style={[styles.modernTextArea, { 
                    backgroundColor: colors.surfaceSecondary, 
                    color: colors.textPrimary,
                    borderColor: colors.border 
                  }]}
                  placeholder="How's your skin feeling today?"
                  placeholderTextColor={colors.textTertiary}
                  value={routineData.daily_note || ''}
                  onChangeText={(text) => setRoutineData(prev => ({
                    ...prev,
                    daily_note: text || undefined
                  }))}
                  multiline
                  numberOfLines={4}
                />
              </View>

              <View style={{ height: 20 }} />
            </ScrollView>
            
            {/* Fixed Bottom Buttons */}
            <View style={[styles.modalFooter, { backgroundColor: colors.background, borderTopColor: colors.border }]}>
              <View style={styles.buttonGroup}>
                <TouchableOpacity
                  style={[styles.skipButton, { backgroundColor: colors.surfaceSecondary, borderColor: colors.border }]}
                  onPress={handleSkipRoutine}
                >
                  <Text style={[styles.skipButtonText, { color: colors.textSecondary }]}>
                    Skip for Now
                  </Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={styles.analyzeButton}
                  onPress={handleAnalyzeImage}
                  disabled={isCapturing}
                >
                  <LinearGradient
                    colors={[Colors.primary, Colors.accent]}
                    style={styles.analyzeButtonGradient}
                  >
                    {isCapturing ? (
                      <ActivityIndicator size="small" color="#FFFFFF" />
                    ) : (
                      <>
                        <CustomIcon name="sparkles" size={20} color="#FFFFFF" />
                        <Text style={styles.analyzeButtonText}>
                          Analyze Now
                        </Text>
                      </>
                    )}
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

// ============================================================================
// STYLES
// ============================================================================
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 100,
  },
  
  // Header
  modernHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modernTitle: {
    fontSize: 20,
    fontWeight: '700',
  },
  headerSpacer: {
    width: 44,
  },
  
  // Hero
  heroSection: {
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 30,
  },
  heroGradient: {
    borderRadius: 80,
    padding: 30,
    marginBottom: 24,
  },
  cameraHero: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 10,
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 8,
  },
  heroSubtitle: {
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
  },
  
  // Actions
  actionGrid: {
    paddingHorizontal: 20,
    gap: 12,
    marginBottom: 24,
  },
  primaryActionButton: {
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  buttonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    paddingHorizontal: 24,
    gap: 12,
  },
  primaryButtonText: {
    fontSize: 17,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  secondaryActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    paddingHorizontal: 24,
    borderRadius: 16,
    borderWidth: 2,
    gap: 12,
  },
  secondaryButtonText: {
    fontSize: 17,
    fontWeight: '600',
  },
  
  // Tips
  tipsCard: {
    marginHorizontal: 20,
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
  },
  tipsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 10,
  },
  tipsIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  tipsTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  tipsList: {
    gap: 12,
  },
  tipRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  tipBullet: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  tipBulletText: {
    fontSize: 12,
    fontWeight: '700',
  },
  tipText: {
    flex: 1,
    fontSize: 15,
    lineHeight: 22,
  },
  
  // SMOOTH SLIDER STYLES
  sliderContainer: {
    marginBottom: 32,
    paddingHorizontal: 4,
  },
  sliderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  sliderLabelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  labelText: {
    fontSize: 17,
    fontWeight: '700',
  },
  valueChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 2,
    gap: 4,
  },
  valueNumber: {
    fontSize: 22,
    fontWeight: '800',
  },
  valueUnit: {
    fontSize: 14,
    fontWeight: '600',
  },
  trackContainer: {
    position: 'relative',
    height: 50,
    justifyContent: 'center',
    marginBottom: 12,
  },
  trackWrapper: {
    width: '100%',
  },
  track: {
    height: 12,
    borderRadius: 6,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  trackFill: {
    height: '100%',
    borderRadius: 6,
  },
  thumb: {
    position: 'absolute',
    width: 40,
    height: 40,
    borderRadius: 20,
    top: 5,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: '#FFFFFF',
    shadowOffset: { width: 0, height: 4 },
  },
  thumbInner: {
    width: 20,
    height: 20,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  thumbDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  rangeLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 4,
  },
  rangeLabel: {
    fontSize: 13,
    fontWeight: '600',
  },
  rangeDivider: {
    flex: 1,
    height: 1,
    backgroundColor: 'rgba(0,0,0,0.05)',
    marginHorizontal: 16,
  },
  
  // Modal
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'flex-end',
  },
  premiumModal: {
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    minHeight: '75%',
    maxHeight: '90%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 20,
  },
  modalHandle: {
    width: 40,
    height: 5,
    borderRadius: 3,
    alignSelf: 'center',
    marginTop: 12,
    marginBottom: 8,
  },
  premiumModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 24,
  },
  modalMainTitle: {
    fontSize: 26,
    fontWeight: '800',
    marginBottom: 4,
  },
  modalMainSubtitle: {
    fontSize: 15,
    fontWeight: '500',
  },
  closeButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalScroll: {
    flex: 1,
  },
  modalScrollContent: {
    paddingHorizontal: 24,
    paddingBottom: 20,
  },
  modalFooter: {
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 32,
    borderTopWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  
  // Input Sections
  inputSection: {
    marginBottom: 24,
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
  },
  inputHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 10,
  },
  inputIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  inputTitle: {
    fontSize: 17,
    fontWeight: '700',
  },
  modernTextArea: {
    borderRadius: 16,
    padding: 16,
    fontSize: 15,
    lineHeight: 22,
    minHeight: 100,
    textAlignVertical: 'top',
    borderWidth: 2,
  },
  
  // Button Group
  buttonGroup: {
    flexDirection: 'row',
    gap: 12,
  },
  skipButton: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 16,
    borderWidth: 2,
    justifyContent: 'center',
    alignItems: 'center',
  },
  skipButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  analyzeButton: {
    flex: 2,
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  analyzeButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 8,
  },
  analyzeButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  
  // Welcome Modal Styles
  welcomeModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  welcomeModalContent: {
    width: '100%',
    maxWidth: 400,
    borderRadius: 24,
    overflow: 'hidden',
    ...Shadows.large,
  },
  welcomeCloseButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(0, 0, 0, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  welcomeModalHeader: {
    paddingTop: 56,
    paddingBottom: 28,
    paddingHorizontal: 24,
    alignItems: 'center',
  },
  welcomeIconContainer: {
    width: 104,
    height: 104,
    borderRadius: 52,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  welcomeModalBody: {
    padding: 24,
  },
  welcomeTitle: {
    fontSize: 26,
    fontWeight: '800',
    marginBottom: 12,
    textAlign: 'center',
  },
  welcomeMessage: {
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 24,
    textAlign: 'center',
  },
  welcomeFeatures: {
    marginBottom: 24,
  },
  welcomeFeature: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  welcomeFeatureIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  welcomeFeatureText: {
    fontSize: 15,
    fontWeight: '600',
    flex: 1,
  },
  welcomeNote: {
    fontSize: 13,
    lineHeight: 20,
    marginBottom: 24,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  welcomeActionButton: {
    borderRadius: 16,
    overflow: 'hidden',
    ...Shadows.medium,
  },
  welcomeActionGradient: {
    flexDirection: 'row',
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  welcomeActionText: {
    fontSize: 17,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});

export default SimpleCameraScreen;

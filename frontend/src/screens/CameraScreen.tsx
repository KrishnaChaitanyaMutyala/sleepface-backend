import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
  Animated,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import { Camera, CameraType } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import CustomIcon from '../components/CustomIcon';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { useAnalysis } from '../contexts/AnalysisContext';
import { useTheme } from '../contexts/ThemeContext';
import { RoutineData } from '../types';
import { Colors, getThemeColors } from '../design/DesignSystem';

const { width, height } = Dimensions.get('window');

// ============================================================================
// ANIMATED FACE GUIDE COMPONENT
// ============================================================================
const AnimatedFaceGuide: React.FC<{ ready: boolean }> = ({ ready }) => {
  const scaleAnim = useRef(new Animated.Value(0.9)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Breathing animation
    Animated.loop(
      Animated.sequence([
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 0.95,
          duration: 2000,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Fade in
    Animated.timing(opacityAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, []);

  return (
    <Animated.View
      style={[
        styles.faceGuide,
        {
          transform: [{ scale: scaleAnim }],
          opacity: opacityAnim,
          borderColor: ready ? '#10B981' : '#6366F1',
        },
      ]}
    >
      <View style={[styles.faceGuideInner, { borderColor: ready ? '#10B98150' : '#6366F150' }]} />
      
      {/* Corner Indicators */}
      <View style={[styles.cornerTL, { borderColor: ready ? '#10B981' : '#6366F1' }]} />
      <View style={[styles.cornerTR, { borderColor: ready ? '#10B981' : '#6366F1' }]} />
      <View style={[styles.cornerBL, { borderColor: ready ? '#10B981' : '#6366F1' }]} />
      <View style={[styles.cornerBR, { borderColor: ready ? '#10B981' : '#6366F1' }]} />
    </Animated.View>
  );
};

// ============================================================================
// CAPTURE BUTTON COMPONENT
// ============================================================================
const CaptureButton: React.FC<{
  onPress: () => void;
  disabled: boolean;
  loading: boolean;
}> = ({ onPress, disabled, loading }) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.9,
      useNativeDriver: true,
      tension: 100,
      friction: 3,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      tension: 100,
      friction: 3,
    }).start();
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      disabled={disabled || loading}
      activeOpacity={1}
    >
      <Animated.View
        style={[
          styles.captureButton,
          {
            transform: [{ scale: scaleAnim }],
            opacity: disabled ? 0.5 : 1,
          },
        ]}
      >
        {loading ? (
          <ActivityIndicator size="large" color={Colors.primary} />
        ) : (
          <View style={styles.captureButtonInner}>
            <LinearGradient
              colors={[Colors.primary, Colors.accent]}
              style={styles.captureButtonGradient}
            />
          </View>
        )}
      </Animated.View>
    </TouchableOpacity>
  );
};

// ============================================================================
// MAIN CAMERA SCREEN COMPONENT
// ============================================================================
const CameraScreen: React.FC = () => {
  const navigation = useNavigation();
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const { analyzeImage, isLoading } = useAnalysis();
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [cameraType, setCameraType] = useState(CameraType.front);
  const [isCapturing, setIsCapturing] = useState(false);
  const [flashMode, setFlashMode] = useState<'off' | 'on' | 'auto'>('off');
  const [cameraReady, setCameraReady] = useState(false);
  const cameraRef = useRef<Camera>(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    getCameraPermissions();
    
    // Fade in animation
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, []);

  const getCameraPermissions = async () => {
    try {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
      
      if (status !== 'granted') {
        Alert.alert(
          'Camera Permission Required',
          'Please enable camera access to take selfies for analysis.',
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Open Settings', onPress: () => getCameraPermissions() }
          ]
        );
      }
    } catch (error) {
      console.error('Error requesting camera permission:', error);
      setHasPermission(false);
    }
  };

  const takePicture = async () => {
    if (isCapturing || !cameraRef.current || !cameraReady) return;

    try {
      setIsCapturing(true);
      
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: false,
        skipProcessing: false,
      });

      if (photo?.uri) {
        // For now, use default routine data - you can add a modal here
        const routineData: RoutineData = {
          sleep_hours: 7.5,
          water_intake: 8,
          product_used: undefined,
          skincare_products: [],
          daily_note: undefined,
        };
        
        await analyzeImage(photo.uri, routineData);
        navigation.navigate('Analysis' as never);
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
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]?.uri) {
        const routineData: RoutineData = {
          sleep_hours: 7.5,
          water_intake: 8,
          product_used: undefined,
          skincare_products: [],
          daily_note: undefined,
        };
        
        await analyzeImage(result.assets[0].uri, routineData);
        navigation.navigate('Analysis' as never);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to pick image. Please try again.');
    }
  };

  const flipCamera = () => {
    setCameraType(cameraType === CameraType.back ? CameraType.front : CameraType.back);
  };

  const toggleFlash = () => {
    const modes: Array<'off' | 'on' | 'auto'> = ['off', 'on', 'auto'];
    const currentIndex = modes.indexOf(flashMode);
    const nextIndex = (currentIndex + 1) % modes.length;
    setFlashMode(modes[nextIndex]);
  };

  // Permission Loading State
  if (hasPermission === null) {
    return (
      <View style={[styles.permissionContainer, { backgroundColor: colors.background }]}>
        <View style={styles.permissionContent}>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={[styles.permissionText, { color: colors.textPrimary }]}>
            Initializing camera...
          </Text>
        </View>
      </View>
    );
  }

  // Permission Denied State
  if (hasPermission === false) {
    return (
      <SafeAreaView style={[styles.permissionContainer, { backgroundColor: colors.background }]}>
        <StatusBar barStyle={isDark ? "light-content" : "dark-content"} />
        
        <View style={styles.permissionContent}>
          <View style={[styles.permissionIcon, { backgroundColor: Colors.primary + '15' }]}>
            <CustomIcon name="camera" size={64} color={Colors.primary} />
          </View>
          
          <Text style={[styles.permissionTitle, { color: colors.textPrimary }]}>
            Camera Access Required
          </Text>
          <Text style={[styles.permissionSubtitle, { color: colors.textSecondary }]}>
            We need camera access to capture your selfie for skin and sleep analysis
          </Text>
          
          <TouchableOpacity style={styles.permissionButton} onPress={getCameraPermissions}>
            <LinearGradient
              colors={[Colors.primary, Colors.accent]}
              style={styles.permissionButtonGradient}
            >
              <CustomIcon name="camera" size={20} color="#FFFFFF" />
              <Text style={styles.permissionButtonText}>Grant Permission</Text>
            </LinearGradient>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.galleryButton, { borderColor: colors.border }]}
            onPress={pickFromGallery}
          >
            <CustomIcon name="image" size={20} color={Colors.primary} />
            <Text style={[styles.galleryButtonText, { color: Colors.primary }]}>
              Choose from Gallery
            </Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // Main Camera View
  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="transparent" translucent />
      
      {/* Camera */}
      <Camera
        ref={cameraRef}
        style={styles.camera}
        type={cameraType}
        flashMode={flashMode}
        ratio="16:9"
        onCameraReady={() => setCameraReady(true)}
        onMountError={(error) => {
          console.error('Camera error:', error);
          Alert.alert('Camera Error', 'Failed to initialize camera.');
        }}
      >
        <Animated.View style={[styles.cameraOverlay, { opacity: fadeAnim }]}>
          {/* Top Bar */}
          <LinearGradient
            colors={['rgba(0,0,0,0.8)', 'transparent']}
            style={styles.topBar}
          >
            <TouchableOpacity style={styles.topButton} onPress={() => navigation.goBack()}>
              <CustomIcon name="close" size={24} color="#FFFFFF" />
            </TouchableOpacity>
            
            <Text style={styles.topTitle}>Take Selfie</Text>
            
            <TouchableOpacity style={styles.topButton} onPress={pickFromGallery}>
              <CustomIcon name="image" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </LinearGradient>

          {/* Face Guide */}
          <View style={styles.guideContainer}>
            <AnimatedFaceGuide ready={cameraReady} />
            
            {/* Instructions */}
            <View style={styles.instructionsContainer}>
              <View style={[styles.instructionBadge, { backgroundColor: cameraReady ? '#10B98120' : '#6366F120' }]}>
                <CustomIcon 
                  name={cameraReady ? "check" : "info"} 
                  size={16} 
                  color={cameraReady ? '#10B981' : '#6366F1'} 
                />
                <Text style={[styles.instructionBadgeText, { color: cameraReady ? '#10B981' : '#6366F1' }]}>
                  {cameraReady ? 'Camera Ready' : 'Initializing...'}
                </Text>
              </View>
              
              <Text style={styles.instructionText}>
                Position your face in the frame
              </Text>
              <Text style={styles.instructionSubtext}>
                Ensure good lighting for best results
              </Text>
            </View>
          </View>

          {/* Bottom Controls */}
          <LinearGradient
            colors={['transparent', 'rgba(0,0,0,0.9)']}
            style={styles.bottomBar}
          >
            {/* Control Buttons */}
            <View style={styles.controlsRow}>
              <TouchableOpacity style={styles.controlButton} onPress={toggleFlash}>
                <View style={styles.controlButtonInner}>
                  <CustomIcon
                    name={flashMode === 'off' ? 'zap-off' : flashMode === 'on' ? 'zap' : 'zap'}
                    size={24}
                    color="#FFFFFF"
                  />
                  <Text style={styles.controlButtonLabel}>
                    {flashMode === 'off' ? 'Off' : flashMode === 'on' ? 'On' : 'Auto'}
                  </Text>
                </View>
              </TouchableOpacity>

              {/* Capture Button */}
              <CaptureButton
                onPress={takePicture}
                disabled={!cameraReady}
                loading={isCapturing}
              />

              <TouchableOpacity style={styles.controlButton} onPress={flipCamera}>
                <View style={styles.controlButtonInner}>
                  <CustomIcon name="refresh-cw" size={24} color="#FFFFFF" />
                  <Text style={styles.controlButtonLabel}>Flip</Text>
                </View>
              </TouchableOpacity>
            </View>

            {/* Tips */}
            <View style={styles.tipsContainer}>
              <View style={styles.tipItem}>
                <View style={styles.tipDot} />
                <Text style={styles.tipText}>Good lighting</Text>
              </View>
              <View style={styles.tipItem}>
                <View style={styles.tipDot} />
                <Text style={styles.tipText}>Face forward</Text>
              </View>
              <View style={styles.tipItem}>
                <View style={styles.tipDot} />
                <Text style={styles.tipText}>Remove glasses</Text>
              </View>
            </View>
          </LinearGradient>
        </Animated.View>
      </Camera>
    </View>
  );
};

// ============================================================================
// STYLES
// ============================================================================
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    flex: 1,
  },
  
  // Top Bar
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  topButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  topTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  
  // Face Guide
  guideContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  faceGuide: {
    width: 280,
    height: 350,
    borderRadius: 140,
    borderWidth: 3,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  faceGuideInner: {
    width: 260,
    height: 330,
    borderRadius: 130,
    borderWidth: 2,
  },
  
  // Corner Indicators
  cornerTL: {
    position: 'absolute',
    top: -2,
    left: -2,
    width: 30,
    height: 30,
    borderTopWidth: 4,
    borderLeftWidth: 4,
    borderTopLeftRadius: 140,
  },
  cornerTR: {
    position: 'absolute',
    top: -2,
    right: -2,
    width: 30,
    height: 30,
    borderTopWidth: 4,
    borderRightWidth: 4,
    borderTopRightRadius: 140,
  },
  cornerBL: {
    position: 'absolute',
    bottom: -2,
    left: -2,
    width: 30,
    height: 30,
    borderBottomWidth: 4,
    borderLeftWidth: 4,
    borderBottomLeftRadius: 140,
  },
  cornerBR: {
    position: 'absolute',
    bottom: -2,
    right: -2,
    width: 30,
    height: 30,
    borderBottomWidth: 4,
    borderRightWidth: 4,
    borderBottomRightRadius: 140,
  },
  
  // Instructions
  instructionsContainer: {
    position: 'absolute',
    bottom: -100,
    alignItems: 'center',
    gap: 8,
  },
  instructionBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  instructionBadgeText: {
    fontSize: 13,
    fontWeight: '700',
  },
  instructionText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  instructionSubtext: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.7)',
  },
  
  // Bottom Bar
  bottomBar: {
    paddingTop: 30,
    paddingBottom: 50,
    paddingHorizontal: 20,
  },
  controlsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  controlButton: {
    width: 70,
    alignItems: 'center',
  },
  controlButtonInner: {
    alignItems: 'center',
    gap: 6,
  },
  controlButtonLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  
  // Capture Button
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  captureButtonInner: {
    width: 68,
    height: 68,
    borderRadius: 34,
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButtonGradient: {
    width: '100%',
    height: '100%',
  },
  
  // Tips
  tipsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 20,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  tipDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: Colors.primary,
  },
  tipText: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
    fontWeight: '500',
  },
  
  // Permission States
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  permissionContent: {
    alignItems: 'center',
    paddingHorizontal: 40,
    maxWidth: 400,
  },
  permissionIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  permissionTitle: {
    fontSize: 24,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 8,
  },
  permissionSubtitle: {
    fontSize: 15,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 32,
  },
  permissionText: {
    fontSize: 16,
    marginTop: 16,
  },
  permissionButton: {
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 12,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  permissionButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 32,
    gap: 10,
  },
  permissionButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  galleryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 16,
    borderWidth: 2,
    gap: 10,
  },
  galleryButtonText: {
    fontSize: 16,
    fontWeight: '700',
  },
});

export default CameraScreen;

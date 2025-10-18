import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Animated,
  Dimensions,
  Modal,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';
import { useAnalysis } from '../contexts/AnalysisContext';
import { useTheme } from '../contexts/ThemeContext';
import { AnalysisResult, DailySummary } from '../types';
import CustomIcon from '../components/CustomIcon';
import { FeatureIcon } from '../components/FeatureIcon';
import { stripEmojis } from '../utils/iconMapping';
import { Colors, Typography, Spacing, BorderRadius, Shadows, getScoreColor, getScoreLabel, getThemeColors, ButtonStyles } from '../design/DesignSystem';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

// ============================================================================
// ANIMATED SCORE RING COMPONENT
// ============================================================================
const ScoreRing: React.FC<{
  score: number;
  label: string;
  color: string;
  size?: number;
}> = ({ score, label, color, size = 120 }) => {
  const animatedValue = React.useRef(new Animated.Value(0)).current;
  const circumference = (size - 12) * Math.PI;
  const strokeDashoffset = circumference - (circumference * score) / 100;

  React.useEffect(() => {
    Animated.spring(animatedValue, {
      toValue: score,
      useNativeDriver: true,
      tension: 40,
      friction: 7,
    }).start();
  }, [score]);

  return (
    <View style={[styles.scoreRingContainer, { width: size, height: size }]}>
      {/* Background Circle */}
      <View style={[styles.scoreRingBg, { 
        width: size - 12, 
        height: size - 12,
        borderRadius: (size - 12) / 2,
        borderColor: color + '20',
      }]} />
      
      {/* Progress Circle - SVG alternative using border */}
      <View style={[styles.scoreRingProgress, {
        width: size - 12,
        height: size - 12,
        borderRadius: (size - 12) / 2,
        borderColor: color,
        borderWidth: 6,
        transform: [{ rotate: '-90deg' }],
      }]} />
      
      {/* Score Text */}
      <View style={styles.scoreRingContent}>
        <Text style={[styles.scoreRingNumber, { color }]}>
          {Math.round(score)}
        </Text>
        <Text style={styles.scoreRingLabel}>{label}</Text>
      </View>
    </View>
  );
};

// ============================================================================
// FEATURE BADGE COMPONENT
// ============================================================================
const FeatureBadge: React.FC<{
  icon: string;
  label: string;
  value: number;
  color: string;
}> = ({ icon, label, value, color }) => (
  <View style={[styles.featureBadge, { borderColor: color + '30' }]}>
    <View style={[styles.featureBadgeIcon, { backgroundColor: color + '15' }]}>
      <CustomIcon name={icon as keyof typeof import('../design/DesignSystem').Icons} size={20} color={color} />
    </View>
    <View style={styles.featureBadgeContent}>
      <Text style={styles.featureBadgeLabel}>{label}</Text>
      <Text style={[styles.featureBadgeValue, { color }]}>{value}</Text>
    </View>
  </View>
);

// ============================================================================
// GUEST WELCOME MODAL
// ============================================================================
const GuestWelcomeModal: React.FC<{
  visible: boolean;
  onClose: () => void;
  onSignUp: () => void;
}> = ({ visible, onClose, onSignUp }) => {
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const scaleAnim = React.useRef(new Animated.Value(0.8)).current;
  const opacityAnim = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
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

            {/* Action Buttons */}
            <TouchableOpacity style={styles.welcomeSignUpButton} onPress={onSignUp}>
              <LinearGradient
                colors={[Colors.primary, Colors.accent]}
                style={styles.welcomeSignUpGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
              >
                <CustomIcon name="user-plus" size={20} color="#FFFFFF" />
                <Text style={styles.welcomeSignUpText}>Sign Up Free</Text>
              </LinearGradient>
            </TouchableOpacity>

            <TouchableOpacity style={styles.welcomeContinueButton} onPress={onClose}>
              <Text style={[styles.welcomeContinueText, { color: colors.textSecondary }]}>
                Continue as Guest
              </Text>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </View>
    </Modal>
  );
};

// ============================================================================
// MAIN HOME SCREEN COMPONENT
// ============================================================================
const HomeScreen: React.FC = () => {
  const navigation = useNavigation();
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const { user, isGuest } = useAuth();
  const { 
    currentAnalysis, 
    dailySummary, 
    weeklyAnalysis,
    streakData, 
    isLoading,
    getDailySummary,
    getAnalysisHistory,
    getWeeklyAnalysis
  } = useAnalysis();
  
  const [refreshing, setRefreshing] = useState(false);
  const fadeAnim = React.useRef(new Animated.Value(0)).current;

  useEffect(() => {
    loadTodayData();
    loadWeeklyAnalysis();
    
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start();
  }, []);

  const loadTodayData = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      await getDailySummary(today);
      await getAnalysisHistory(7);
    } catch (error) {
      console.error('Error loading today data:', error);
    }
  };

  const loadWeeklyAnalysis = async () => {
    try {
      await getWeeklyAnalysis(7);
    } catch (error) {
      console.error('Error loading weekly analysis:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTodayData();
    await loadWeeklyAnalysis();
    setRefreshing(false);
  };

  const handleScanPress = () => {
    navigation.navigate('Camera' as never);
  };

  const handleAnalysisPress = () => {
    if (currentAnalysis) {
      navigation.navigate('Analysis' as never);
    } else {
      Alert.alert(
        'No Analysis Yet',
        'Take a selfie to see your sleep and skin health scores!',
        [{ text: 'OK' }]
      );
    }
  };

  const getTimeGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return '🌅 Good Morning';
    if (hour < 18) return '☀️ Good Afternoon';
    return '🌙 Good Evening';
  };

  return (
    <ScrollView 
        style={[styles.container, { backgroundColor: colors.background }]}
      refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={onRefresh}
            tintColor={Colors.primary}
          />
        }
        showsVerticalScrollIndicator={false}
      >
      {/* Premium Header with Gradient */}
      <LinearGradient
        colors={[Colors.primary, Colors.accent]}
        style={styles.premiumHeader}
      >
        <View style={styles.headerTop}>
          <View style={styles.headerLeft}>
            <Text style={styles.greetingTime}>{getTimeGreeting()}</Text>
            <Text style={styles.userName}>
              {isGuest ? 'Guest User' : user?.displayName || 'User'}
            </Text>
      </View>

          <TouchableOpacity 
            style={styles.premiumProfileButton}
            onPress={() => navigation.navigate('Profile' as never)}
          >
      <LinearGradient
              colors={['rgba(255,255,255,0.3)', 'rgba(255,255,255,0.1)']}
              style={styles.profileGradient}
            >
              <CustomIcon name="profile" size={24} color="#FFFFFF" />
            </LinearGradient>
          </TouchableOpacity>
          </View>

        {/* Streak Banner */}
        <View style={styles.streakBanner}>
          <View style={styles.streakBannerLeft}>
            <View style={styles.streakIconContainer}>
              <CustomIcon name="fire" size={28} color="#FF6B35" />
        </View>
            <View>
              <Text style={styles.streakBannerNumber}>
                {streakData.current_streak} Days
        </Text>
              <Text style={styles.streakBannerLabel}>Current Streak 🔥</Text>
            </View>
          </View>
          
          {streakData.longest_streak > 0 && (
            <View style={styles.streakBadge}>
              <CustomIcon name="trophy" size={16} color="#FFD700" />
              <Text style={styles.streakBadgeText}>
                Best: {streakData.longest_streak}
              </Text>
            </View>
          )}
        </View>
      </LinearGradient>

      {/* Main Content Container */}
      <Animated.View style={[styles.contentContainer, { opacity: fadeAnim }]}>
        
        {/* Today's Analysis - Premium Card */}
      {currentAnalysis ? (
          <View style={[styles.analysisCard, { backgroundColor: colors.surface }]}>
            <View style={styles.analysisCardHeader}>
              <View style={styles.analysisHeaderLeft}>
                <View style={[styles.analysisIcon, { backgroundColor: Colors.primary + '15' }]}>
                  <CustomIcon name="analytics" size={24} color={Colors.primary} />
                </View>
                <View>
                  <Text style={[styles.analysisCardTitle, { color: colors.textPrimary }]}>
                    Today's Analysis
              </Text>
                  <Text style={[styles.analysisCardDate, { color: colors.textTertiary }]}>
                    {new Date().toLocaleDateString('en-US', { 
                      weekday: 'short', 
                      month: 'short', 
                      day: 'numeric' 
                    })}
              </Text>
            </View>
              </View>
              
              {/* Status Badge */}
              <View style={[styles.statusBadge, { 
                backgroundColor: getScoreColor((currentAnalysis.sleep_score + currentAnalysis.skin_health_score) / 2) + '20',
                borderColor: getScoreColor((currentAnalysis.sleep_score + currentAnalysis.skin_health_score) / 2) + '40',
              }]}>
                <FeatureIcon 
                  status={currentAnalysis.fun_label} 
                  type="status" 
                  size={16} 
                  color={getScoreColor((currentAnalysis.sleep_score + currentAnalysis.skin_health_score) / 2)} 
                />
                <Text style={[styles.statusBadgeText, { 
                  color: getScoreColor((currentAnalysis.sleep_score + currentAnalysis.skin_health_score) / 2) 
                }]}>
                  {currentAnalysis.fun_label.replace('_', ' ')}
              </Text>
              </View>
            </View>

            {/* Score Rings */}
            <View style={styles.scoreRingsContainer}>
              <TouchableOpacity 
                style={styles.scoreRingWrapper}
                onPress={handleAnalysisPress}
                activeOpacity={0.8}
              >
                <LinearGradient
                  colors={[getScoreColor(currentAnalysis.sleep_score) + '10', 'transparent']}
                  style={styles.scoreRingGradient}
                >
                  <ScoreRing
                    score={currentAnalysis.sleep_score}
                    label="Sleep"
                    color={getScoreColor(currentAnalysis.sleep_score)}
                    size={130}
                  />
                </LinearGradient>
                <Text style={[styles.scoreStatus, { color: colors.textSecondary }]}>
                  {getScoreLabel(currentAnalysis.sleep_score)}
                </Text>
              </TouchableOpacity>

              <View style={styles.scoreRingDivider} />

              <TouchableOpacity 
                style={styles.scoreRingWrapper}
                onPress={handleAnalysisPress}
                activeOpacity={0.8}
              >
                <LinearGradient
                  colors={[getScoreColor(currentAnalysis.skin_health_score) + '10', 'transparent']}
                  style={styles.scoreRingGradient}
                >
                  <ScoreRing
                    score={currentAnalysis.skin_health_score}
                    label="Skin"
                    color={getScoreColor(currentAnalysis.skin_health_score)}
                    size={130}
                  />
                </LinearGradient>
                <Text style={[styles.scoreStatus, { color: colors.textSecondary }]}>
                {getScoreLabel(currentAnalysis.skin_health_score)}
              </Text>
              </TouchableOpacity>
            </View>

            {/* Feature Highlights */}
            {currentAnalysis.features && (
              <View style={styles.featuresGrid}>
                <FeatureBadge
                  icon="eye"
                  label="Dark Circles"
                  value={Math.round(currentAnalysis.features.dark_circles || 0)}
                  color="#5B8DEF"
                />
                <FeatureBadge
                  icon="sparkles"
                  label="Brightness"
                  value={Math.round(currentAnalysis.features.brightness || 0)}
                  color="#FFB84D"
                />
                <FeatureBadge
                  icon="droplet"
                  label="Puffiness"
                  value={Math.round(currentAnalysis.features.puffiness || 0)}
                  color="#4ECDC4"
                />
                <FeatureBadge
                  icon="layers"
                  label="Texture"
                  value={Math.round(currentAnalysis.features.texture || 0)}
                  color="#A78BFA"
                />
          </View>
            )}

            {/* View Details Button */}
            <TouchableOpacity 
              style={[styles.viewDetailsButton, { backgroundColor: Colors.primary + '10' }]}
              onPress={handleAnalysisPress}
              activeOpacity={0.8}
            >
              <Text style={[styles.viewDetailsText, { color: Colors.primary }]}>
                View Full Analysis
              </Text>
              <CustomIcon name="chevronRight" size={20} color={Colors.primary} />
          </TouchableOpacity>
          </View>
      ) : (
          /* Empty State - Premium Design */
          <View style={[styles.emptyStateCard, { backgroundColor: colors.surface }]}>
        <LinearGradient
              colors={[Colors.primary + '20', Colors.accent + '20']}
              style={styles.emptyStateGradient}
            >
              <View style={styles.emptyStateIcon}>
                <CustomIcon name="camera" size={48} color={Colors.primary} />
              </View>
            </LinearGradient>
            
            <Text style={[styles.emptyStateTitle, { color: colors.textPrimary }]}>
              Start Your Journey
          </Text>
            <Text style={[styles.emptyStateDescription, { color: colors.textSecondary }]}>
              Take your first selfie to unlock AI-powered skin and sleep analysis
            </Text>
            
            <TouchableOpacity 
              style={styles.emptyStateCTA}
              onPress={handleScanPress}
              activeOpacity={0.9}
            >
              <LinearGradient
                colors={[Colors.primary, Colors.accent]}
                style={styles.emptyStateCTAGradient}
              >
                <CustomIcon name="camera" size={24} color="#FFFFFF" />
                <Text style={styles.emptyStateCTAText}>Take Your First Selfie</Text>
        </LinearGradient>
            </TouchableOpacity>
          </View>
      )}

        {/* Weekly Insights - Premium Card */}
      {weeklyAnalysis && (
          <View style={[styles.weeklyCard, { backgroundColor: colors.surface }]}>
            <View style={styles.weeklyCardHeader}>
              <View style={styles.weeklyHeaderLeft}>
                <View style={[styles.weeklyIcon, { backgroundColor: Colors.accent + '15' }]}>
                  <CustomIcon name="trend" size={24} color={Colors.accent} />
            </View>
                <Text style={[styles.weeklyCardTitle, { color: colors.textPrimary }]}>
                  Weekly Insights
                </Text>
              </View>
              
              <TouchableOpacity 
                style={styles.weeklyMoreButton}
                onPress={() => navigation.navigate('History' as never)}
              >
                <Text style={[styles.weeklyMoreText, { color: Colors.primary }]}>
                  View All
                </Text>
                <CustomIcon name="chevronRight" size={16} color={Colors.primary} />
              </TouchableOpacity>
          </View>
          
          {isGuest ? (
              /* Guest Prompt - Premium Design */
              <View style={[styles.guestPrompt, { backgroundColor: Colors.primary + '10' }]}>
                <View style={[styles.guestPromptIcon, { backgroundColor: Colors.primary + '20' }]}>
                  <CustomIcon name="lock" size={32} color={Colors.primary} />
              </View>
                <Text style={[styles.guestPromptTitle, { color: colors.textPrimary }]}>
                  Unlock Premium Insights
                </Text>
                <Text style={[styles.guestPromptText, { color: colors.textSecondary }]}>
                  Register to track trends, get personalized recommendations, and see your progress over time
              </Text>
              <TouchableOpacity 
                  style={styles.guestPromptCTA}
                  onPress={() => navigation.navigate('Register' as never)}
                >
                  <LinearGradient
                    colors={[Colors.primary, Colors.accent]}
                    style={styles.guestPromptCTAGradient}
                  >
                    <CustomIcon name="sparkles" size={18} color="#FFFFFF" />
                    <Text style={styles.guestPromptCTAText}>Register Now</Text>
                  </LinearGradient>
              </TouchableOpacity>
            </View>
          ) : (
              /* Weekly Content */
            <View style={styles.weeklyContent}>
                {/* Summary */}
                <View style={[styles.weeklySummary, { backgroundColor: colors.surfaceSecondary }]}>
                  <CustomIcon name="info" size={20} color={Colors.primary} />
                  <Text style={[styles.weeklySummaryText, { color: colors.textSecondary }]}>
                    {weeklyAnalysis.weekly_summary || "Take more selfies this week to get personalized insights!"}
              </Text>
                </View>
              
                {/* Insights List */}
              {weeklyAnalysis.weekly_insights && weeklyAnalysis.weekly_insights.length > 0 && (
                  <View style={styles.insightsList}>
                    <View style={styles.insightsHeader}>
                      <CustomIcon name="lightbulb" size={18} color={Colors.accent} />
                      <Text style={[styles.insightsHeaderText, { color: colors.textPrimary }]}>
                        Key Trends
                      </Text>
                  </View>
                    {weeklyAnalysis.weekly_insights.slice(0, 3).map((insight: string, index: number) => (
                      <View key={index} style={styles.insightRow}>
                        <View style={[styles.insightDot, { backgroundColor: Colors.accent }]} />
                        <Text style={[styles.insightText, { color: colors.textSecondary }]}>
                          {stripEmojis(insight)}
                        </Text>
                    </View>
                  ))}
                </View>
              )}
              
                {/* Recommendations */}
              {weeklyAnalysis.weekly_recommendations && weeklyAnalysis.weekly_recommendations.length > 0 && (
                  <View style={styles.recommendationsList}>
                    <View style={styles.recommendationsHeader}>
                    <CustomIcon name="success" size={18} color={Colors.success} />
                      <Text style={[styles.recommendationsHeaderText, { color: colors.textPrimary }]}>
                        Recommendations
                      </Text>
                  </View>
                    {weeklyAnalysis.weekly_recommendations.slice(0, 3).map((rec: string, index: number) => (
                      <View key={index} style={styles.recommendationRow}>
                        <View style={[styles.recommendationCheck, { backgroundColor: Colors.success + '20' }]}>
                          <CustomIcon name="check" size={12} color={Colors.success} />
                        </View>
                        <Text style={[styles.recommendationText, { color: colors.textSecondary }]}>
                          {stripEmojis(rec)}
                        </Text>
                    </View>
                  ))}
                </View>
              )}

                {/* Medical Disclaimer */}
                <View style={[styles.disclaimerBox, { backgroundColor: Colors.warning + '10', borderColor: Colors.warning + '30' }]}>
                  <View style={styles.disclaimerHeader}>
                    <CustomIcon name="alert-triangle" size={16} color={Colors.warning} />
                    <Text style={[styles.disclaimerTitle, { color: Colors.warning }]}>
                      Important Notice
                    </Text>
                  </View>
                  <Text style={[styles.disclaimerText, { color: colors.textSecondary }]}>
                    AI-generated recommendations are for informational purposes only. Not a substitute for professional medical advice. 
                    Consult a dermatologist before trying new products or treatments. We are not responsible for any results.
                  </Text>
                </View>
            </View>
          )}
          </View>
        )}

        {/* Quick Actions - Premium Floating Buttons */}
        <View style={styles.quickActions}>
          <TouchableOpacity
            style={styles.primaryQuickAction}
            onPress={handleScanPress}
            activeOpacity={0.9}
          >
            <LinearGradient
              colors={[Colors.primary, Colors.accent]}
              style={styles.quickActionGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            >
              <View style={styles.quickActionIconContainer}>
                <CustomIcon name="camera" size={28} color="#FFFFFF" />
              </View>
              <View style={styles.quickActionContent}>
                <Text style={styles.quickActionTitle}>New Scan</Text>
                <Text style={styles.quickActionSubtitle}>Take a selfie</Text>
              </View>
              <CustomIcon name="chevronRight" size={20} color="rgba(255,255,255,0.6)" />
            </LinearGradient>
        </TouchableOpacity>
        
        <TouchableOpacity 
            style={[styles.secondaryQuickAction, { backgroundColor: colors.surface }]}
          onPress={() => navigation.navigate('History' as never)}
            activeOpacity={0.8}
        >
            <View style={[styles.quickActionIconSmall, { backgroundColor: Colors.primary + '15' }]}>
          <CustomIcon name="analytics" size={20} color={Colors.primary} />
            </View>
            <View style={styles.quickActionContentSmall}>
              <Text style={[styles.quickActionTitleSmall, { color: colors.textPrimary }]}>
                History
              </Text>
              <Text style={[styles.quickActionSubtitleSmall, { color: colors.textTertiary }]}>
                View past scans
              </Text>
            </View>
            <CustomIcon name="chevronRight" size={16} color={colors.textTertiary} />
        </TouchableOpacity>
      </View>

      </Animated.View>

      {/* Bottom Spacing for Tab Bar */}
      <View style={{ height: 100 }} />
    </ScrollView>
  );
};

// ============================================================================
// STYLES - Premium, Modern, Professional
// ============================================================================
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  
  // Premium Header
  premiumHeader: {
    paddingTop: 60,
    paddingBottom: 24,
    paddingHorizontal: 20,
    borderBottomLeftRadius: 32,
    borderBottomRightRadius: 32,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 24,
  },
  headerLeft: {
    flex: 1,
  },
  greetingTime: {
    fontSize: 15,
    color: 'rgba(255,255,255,0.9)',
    fontWeight: '500',
    marginBottom: 4,
  },
  userName: {
    fontSize: 28,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  premiumProfileButton: {
    borderRadius: 22,
    overflow: 'hidden',
  },
  profileGradient: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // Streak Banner
  streakBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 16,
    padding: 16,
    // backdropFilter is not supported in React Native
  },
  streakBannerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  streakIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  streakBannerNumber: {
    fontSize: 22,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  streakBannerLabel: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.8)',
    fontWeight: '500',
  },
  streakBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  streakBadgeText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  
  // Content Container
  contentContainer: {
    paddingTop: 20,
    paddingHorizontal: 20,
  },
  
  // Analysis Card
  analysisCard: {
    borderRadius: 24,
    padding: 24,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  analysisCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  analysisHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  analysisIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  analysisCardTitle: {
    fontSize: 20,
    fontWeight: '800',
  },
  analysisCardDate: {
    fontSize: 13,
    marginTop: 2,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
  },
  statusBadgeText: {
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'capitalize',
  },
  
  // Score Rings
  scoreRingsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 24,
  },
  scoreRingWrapper: {
    alignItems: 'center',
  },
  scoreRingGradient: {
    borderRadius: 80,
    padding: 16,
    marginBottom: 8,
  },
  scoreRingContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  scoreRingBg: {
    position: 'absolute',
    borderWidth: 6,
  },
  scoreRingProgress: {
    position: 'absolute',
  },
  scoreRingContent: {
    alignItems: 'center',
  },
  scoreRingNumber: {
    fontSize: 32,
    fontWeight: '800',
  },
  scoreRingLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 2,
  },
  scoreStatus: {
    fontSize: 13,
    fontWeight: '600',
  },
  scoreRingDivider: {
    width: 1,
    height: 80,
    backgroundColor: 'rgba(0,0,0,0.1)',
    alignSelf: 'center',
  },
  
  // Feature Badges
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 16,
  },
  featureBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: 'rgba(0,0,0,0.02)',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1,
    flex: 1,
    minWidth: '47%',
  },
  featureBadgeIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  featureBadgeContent: {
    flex: 1,
  },
  featureBadgeLabel: {
    fontSize: 11,
    color: '#6B7280',
    fontWeight: '500',
  },
  featureBadgeValue: {
    fontSize: 18,
    fontWeight: '800',
  },
  
  // View Details Button
  viewDetailsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  viewDetailsText: {
    fontSize: 15,
    fontWeight: '700',
  },
  
  // Empty State
  emptyStateCard: {
    borderRadius: 24,
    padding: 32,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  emptyStateGradient: {
    borderRadius: 70,
    padding: 24,
    marginBottom: 20,
  },
  emptyStateIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255,255,255,0.9)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyStateTitle: {
    fontSize: 24,
    fontWeight: '800',
    marginBottom: 8,
  },
  emptyStateDescription: {
    fontSize: 15,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 24,
  },
  emptyStateCTA: {
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  emptyStateCTAGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 32,
    gap: 10,
  },
  emptyStateCTAText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  
  // Weekly Card
  weeklyCard: {
    borderRadius: 24,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  weeklyCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  weeklyHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  weeklyIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  weeklyCardTitle: {
    fontSize: 20,
    fontWeight: '800',
  },
  weeklyMoreButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  weeklyMoreText: {
    fontSize: 14,
    fontWeight: '600',
  },
  
  // Guest Prompt
  guestPrompt: {
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
  },
  guestPromptIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  guestPromptTitle: {
    fontSize: 20,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 8,
  },
  guestPromptText: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 20,
  },
  guestPromptCTA: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  guestPromptCTAGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 24,
    gap: 8,
  },
  guestPromptCTAText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  
  // Weekly Content
  weeklyContent: {
    gap: 16,
  },
  weeklySummary: {
    flexDirection: 'row',
    gap: 12,
    padding: 16,
    borderRadius: 12,
  },
  weeklySummaryText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
  
  // Insights List
  insightsList: {
    gap: 12,
  },
  insightsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  insightsHeaderText: {
    fontSize: 16,
    fontWeight: '700',
  },
  insightRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    paddingLeft: 8,
  },
  insightDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginTop: 7,
  },
  insightText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
  
  // Recommendations List
  recommendationsList: {
    gap: 12,
  },
  recommendationsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  recommendationsHeaderText: {
    fontSize: 16,
    fontWeight: '700',
  },
  recommendationRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    paddingLeft: 8,
  },
  recommendationCheck: {
    width: 20,
    height: 20,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 2,
  },
  recommendationText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
  
  // Quick Actions
  quickActions: {
    gap: 12,
  },
  primaryQuickAction: {
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 10,
  },
  quickActionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 20,
    gap: 16,
  },
  quickActionIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  quickActionContent: {
    flex: 1,
  },
  quickActionTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#FFFFFF',
    marginBottom: 2,
  },
  quickActionSubtitle: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.8)',
    fontWeight: '500',
  },
  secondaryQuickAction: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 16,
    gap: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  quickActionIconSmall: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quickActionContentSmall: {
    flex: 1,
  },
  quickActionTitleSmall: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 2,
  },
  quickActionSubtitleSmall: {
    fontSize: 12,
    fontWeight: '500',
  },
  
  // Welcome Modal
  welcomeModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  welcomeModalContent: {
    width: '100%',
    maxWidth: 420,
    borderRadius: 24,
    overflow: 'hidden',
    ...Shadows.large,
  },
  welcomeModalHeader: {
    paddingTop: 48,
    paddingBottom: 32,
    paddingHorizontal: 24,
    alignItems: 'center',
  },
  welcomeIconContainer: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  welcomeModalBody: {
    padding: 24,
  },
  welcomeTitle: {
    fontSize: 28,
    fontWeight: '800',
    marginBottom: 12,
    textAlign: 'center',
  },
  welcomeMessage: {
    fontSize: 16,
    lineHeight: 24,
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
  welcomeSignUpButton: {
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 12,
    ...Shadows.medium,
  },
  welcomeSignUpGradient: {
    flexDirection: 'row',
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  welcomeSignUpText: {
    fontSize: 17,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  welcomeContinueButton: {
    paddingVertical: 14,
    paddingHorizontal: 24,
    alignItems: 'center',
  },
  welcomeContinueText: {
    fontSize: 15,
    fontWeight: '600',
  },
  
  // Disclaimer
  disclaimerBox: {
    marginTop: 16,
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
  },
  disclaimerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 6,
  },
  disclaimerTitle: {
    fontSize: 13,
    fontWeight: '700',
  },
  disclaimerText: {
    fontSize: 11,
    lineHeight: 16,
    fontStyle: 'italic',
  },
});

export default HomeScreen;

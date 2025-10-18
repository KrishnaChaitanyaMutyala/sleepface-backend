import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Share,
  Alert,
  Animated,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { useAnalysis } from '../contexts/AnalysisContext';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { AnalysisResult } from '../types';
import CustomIcon from '../components/CustomIcon';
import { FeatureIcon } from '../components/FeatureIcon';
import { stripEmojis } from '../utils/iconMapping';
import { Colors, Typography, Spacing, BorderRadius, Shadows, getScoreColor, getScoreLabel, getFeatureLabel, getFeatureColor, getThemeColors } from '../design/DesignSystem';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

// ============================================================================
// ANIMATED CIRCULAR PROGRESS COMPONENT
// ============================================================================
const CircularProgress: React.FC<{
  score: number;
  size?: number;
  strokeWidth?: number;
  label: string;
}> = ({ score, size = 140, strokeWidth = 10, label }) => {
  const animatedValue = React.useRef(new Animated.Value(0)).current;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (circumference * score) / 100;
  const color = getScoreColor(score);

  React.useEffect(() => {
    Animated.spring(animatedValue, {
      toValue: score,
      useNativeDriver: false,
      tension: 40,
      friction: 7,
    }).start();
  }, [score]);

  return (
    <View style={[styles.circularProgress, { width: size, height: size }]}>
      {/* Background Circle */}
      <View
        style={[
          styles.circularProgressBg,
          {
            width: size - strokeWidth,
            height: size - strokeWidth,
            borderRadius: (size - strokeWidth) / 2,
            borderWidth: strokeWidth,
            borderColor: color + '20',
          },
        ]}
      />
      
      {/* Progress Circle */}
      <View
        style={[
          styles.circularProgressFill,
          {
            width: size - strokeWidth,
            height: size - strokeWidth,
            borderRadius: (size - strokeWidth) / 2,
            borderWidth: strokeWidth,
            borderColor: color,
          },
        ]}
      />

      {/* Center Content */}
      <View style={styles.circularProgressContent}>
        <Text style={[styles.circularProgressScore, { color }]}>
          {Math.round(score)}
        </Text>
        <Text style={styles.circularProgressLabel}>{label}</Text>
        <Text style={[styles.circularProgressStatus, { color }]}>
          {getScoreLabel(score)}
        </Text>
      </View>
    </View>
  );
};

// ============================================================================
// FEATURE CARD COMPONENT
// ============================================================================
const FeatureCard: React.FC<{
  feature: string;
  value: number;
  colors: any;
}> = ({ feature, value, colors }) => {
  const featureColor = getFeatureColor(value);
  const percentage = Math.min(Math.max(value, 0), 100);

  const getFeatureIcon = (feature: string): keyof typeof import('../design/DesignSystem').Icons => {
    const icons: { [key: string]: keyof typeof import('../design/DesignSystem').Icons } = {
      dark_circles: 'darkCircles',
      puffiness: 'puffiness',
      brightness: 'brightness',
      wrinkles: 'wrinkles',
      texture: 'texture',
      pore_size: 'texture',
    };
    return icons[feature] || 'info';
  };

  const getFeatureStatus = (value: number) => {
    if (value >= 80) return 'Excellent';
    if (value >= 60) return 'Good';
    if (value >= 40) return 'Fair';
    return 'Needs Work';
  };

  return (
    <View style={[styles.featureCard, { backgroundColor: colors.surface }]}>
      <View style={styles.featureCardHeader}>
        <View style={[styles.featureCardIcon, { backgroundColor: featureColor + '15' }]}>
          <CustomIcon name={getFeatureIcon(feature)} size={24} color={featureColor} />
        </View>
        <View style={styles.featureCardInfo}>
          <Text style={[styles.featureCardName, { color: colors.textPrimary }]}>
            {getFeatureLabel(feature)}
          </Text>
          <Text style={[styles.featureCardStatus, { color: featureColor }]}>
            {getFeatureStatus(value)}
          </Text>
        </View>
        <View style={styles.featureCardScore}>
          <Text style={[styles.featureCardScoreValue, { color: featureColor }]}>
            {Math.round(value)}
          </Text>
          <Text style={[styles.featureCardScoreMax, { color: colors.textTertiary }]}>
            /100
          </Text>
        </View>
      </View>

      {/* Progress Bar */}
      <View style={[styles.featureCardBar, { backgroundColor: colors.surfaceSecondary }]}>
        <LinearGradient
          colors={[featureColor, featureColor + 'CC']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={[styles.featureCardBarFill, { width: `${percentage}%` }]}
        />
      </View>
    </View>
  );
};

// ============================================================================
// MAIN ANALYSIS SCREEN COMPONENT
// ============================================================================
const AnalysisScreen: React.FC = () => {
  const navigation = useNavigation();
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const { currentAnalysis } = useAnalysis();
  const { isGuest } = useAuth();
  const [summary, setSummary] = useState<any>(null);
  const fadeAnim = React.useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (currentAnalysis) {
      if (currentAnalysis.smart_summary) {
        setSummary(currentAnalysis.smart_summary);
      } else {
        setSummary(generateBasicSummary(currentAnalysis));
      }
    }

    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start();
  }, [currentAnalysis]);

  const generateBasicSummary = (analysis: AnalysisResult) => {
    if (analysis.smart_summary) {
      return {
        daily_summary: analysis.smart_summary.daily_summary || "Analysis completed successfully.",
        key_insights: analysis.smart_summary.key_insights || [],
        recommendations: analysis.smart_summary.recommendations || []
      };
    }

    const sleepScore = analysis.sleep_score;
    const skinScore = analysis.skin_health_score;
    const avgScore = (sleepScore + skinScore) / 2;

    let dailySummary = "";
    if (avgScore >= 80) {
      dailySummary = `Outstanding! Your Sleep Score (${sleepScore}) and Skin Health (${skinScore}) are excellent. Keep up your amazing routine!`;
    } else if (avgScore >= 60) {
      dailySummary = `Great progress! Your Sleep Score (${sleepScore}) and Skin Health (${skinScore}) show solid results with room for optimization.`;
    } else if (avgScore >= 40) {
      dailySummary = `Good foundation! Your Sleep Score (${sleepScore}) and Skin Health (${skinScore}) have potential for improvement with targeted care.`;
    } else {
      dailySummary = `Let's improve together! Your Sleep Score (${sleepScore}) and Skin Health (${skinScore}) can benefit from focused lifestyle adjustments.`;
    }

    return {
      daily_summary: dailySummary,
      key_insights: [
        "Take daily selfies to track your progress",
        "Maintain consistent sleep schedule for best results",
        "Stay hydrated with 8+ glasses of water daily"
      ],
      recommendations: [
        "Establish a regular bedtime routine",
        "Use gentle skincare products suitable for your skin type",
        "Protect your skin with SPF 30+ sunscreen daily"
      ]
    };
  };

  if (!currentAnalysis) {
    return (
      <View style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.emptyState}>
          <View style={[styles.emptyStateIcon, { backgroundColor: Colors.primary + '10' }]}>
            <CustomIcon name="camera" size={64} color={Colors.primary} />
          </View>
          <Text style={[styles.emptyStateTitle, { color: colors.textPrimary }]}>
            No Analysis Yet
          </Text>
          <Text style={[styles.emptyStateText, { color: colors.textSecondary }]}>
            Take your first selfie to see detailed analysis of your sleep and skin health
          </Text>
          <TouchableOpacity
            style={styles.emptyStateCTA}
            onPress={() => navigation.navigate('Camera' as never)}
          >
            <LinearGradient
              colors={[Colors.primary, Colors.accent]}
              style={styles.emptyStateCTAGradient}
            >
              <CustomIcon name="camera" size={20} color="#FFFFFF" />
              <Text style={styles.emptyStateCTAText}>Take Selfie</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  const handleShare = async () => {
    try {
      await Share.share({
        message: `My Sleep Face Analysis 😴✨\n\nSleep Score: ${currentAnalysis.sleep_score}/100\nSkin Health: ${currentAnalysis.skin_health_score}/100\nStatus: ${currentAnalysis.fun_label}\n\nTrack your wellness journey!`,
        title: 'Sleep Face Analysis',
      });
    } catch (error) {
      console.error('Error sharing:', error);
    }
  };


  return (
    <ScrollView 
      style={[styles.container, { backgroundColor: colors.background }]}
      showsVerticalScrollIndicator={false}
    >
      {/* Premium Header */}
      <LinearGradient
        colors={[Colors.primary, Colors.accent]}
        style={styles.premiumHeader}
      >
        <View style={styles.headerTop}>
          <TouchableOpacity
            style={styles.headerBackButton}
            onPress={() => navigation.goBack()}
          >
            <CustomIcon name="chevronLeft" size={24} color="#FFFFFF" />
          </TouchableOpacity>

          <View style={styles.headerCenter}>
            <Text style={styles.headerTitle}>Analysis Results</Text>
            <Text style={styles.headerDate}>
              {new Date(currentAnalysis.date).toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'short',
                day: 'numeric',
              })}
            </Text>
          </View>

          <TouchableOpacity style={styles.headerShareButton} onPress={handleShare}>
            <CustomIcon name="share" size={20} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

        {/* Status Badge */}
        <View style={styles.statusBadge}>
          <FeatureIcon 
            status={currentAnalysis.fun_label} 
            type="status" 
            size={24} 
            color="#FFFFFF" 
          />
          <Text style={styles.statusBadgeText}>
            {currentAnalysis.fun_label.replace('_', ' ').toUpperCase()}
          </Text>
        </View>
      </LinearGradient>

      <Animated.View style={[styles.content, { opacity: fadeAnim }]}>
        {/* Score Rings */}
        <View style={[styles.scoresSection, { backgroundColor: colors.surface }]}>
          <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
            Your Scores
          </Text>
          
          <View style={styles.scoreRingsContainer}>
            <CircularProgress
              score={currentAnalysis.sleep_score}
              label="Sleep"
              size={140}
            />
            <CircularProgress
              score={currentAnalysis.skin_health_score}
              label="Skin"
              size={140}
            />
          </View>
        </View>

        {/* Features Grid */}
        <View style={styles.featuresSection}>
          <View style={styles.sectionHeader}>
            <View style={[styles.sectionIcon, { backgroundColor: Colors.primary + '15' }]}>
              <CustomIcon name="analytics" size={20} color={Colors.primary} />
            </View>
            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              Detailed Analysis
            </Text>
          </View>

          <View style={styles.featuresGrid}>
            {Object.entries(currentAnalysis.features).map(([feature, value]) => (
              <FeatureCard
                key={feature}
                feature={feature}
                value={value}
                colors={colors}
              />
            ))}
          </View>
        </View>

        {/* Routine Info */}
        {currentAnalysis.routine && (
          <View style={[styles.routineSection, { backgroundColor: colors.surface }]}>
            <View style={styles.sectionHeader}>
              <View style={[styles.sectionIcon, { backgroundColor: Colors.accent + '15' }]}>
                <CustomIcon name="calendar" size={20} color={Colors.accent} />
              </View>
              <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
                Daily Routine
              </Text>
            </View>

            <View style={styles.routineGrid}>
              {currentAnalysis.routine.sleep_hours && (
                <View style={[styles.routineItem, { backgroundColor: colors.surfaceSecondary }]}>
                  <View style={[styles.routineIconContainer, { backgroundColor: '#5B8DEF15' }]}>
                    <CustomIcon name="moon" size={20} color="#5B8DEF" />
                  </View>
                  <View style={styles.routineContent}>
                    <Text style={[styles.routineLabel, { color: colors.textTertiary }]}>
                      Sleep
                    </Text>
                    <Text style={[styles.routineValue, { color: colors.textPrimary }]}>
                      {currentAnalysis.routine.sleep_hours}h
                    </Text>
                  </View>
                </View>
              )}

              {currentAnalysis.routine.water_intake && (
                <View style={[styles.routineItem, { backgroundColor: colors.surfaceSecondary }]}>
                  <View style={[styles.routineIconContainer, { backgroundColor: '#4ECDC415' }]}>
                    <CustomIcon name="droplet" size={20} color="#4ECDC4" />
                  </View>
                  <View style={styles.routineContent}>
                    <Text style={[styles.routineLabel, { color: colors.textTertiary }]}>
                      Water
                    </Text>
                    <Text style={[styles.routineValue, { color: colors.textPrimary }]}>
                      {currentAnalysis.routine.water_intake} glasses
                    </Text>
                  </View>
                </View>
              )}

              {currentAnalysis.routine.skincare_products && 
               currentAnalysis.routine.skincare_products.length > 0 && (
                <View style={[styles.routineItemFull, { backgroundColor: colors.surfaceSecondary }]}>
                  <View style={[styles.routineIconContainer, { backgroundColor: '#A78BFA15' }]}>
                    <CustomIcon name="sparkles" size={20} color="#A78BFA" />
                  </View>
                  <View style={styles.routineContent}>
                    <Text style={[styles.routineLabel, { color: colors.textTertiary }]}>
                      Products Used
                    </Text>
                    <Text style={[styles.routineValue, { color: colors.textPrimary }]}>
                      {currentAnalysis.routine.skincare_products.join(', ')}
                    </Text>
                  </View>
                </View>
              )}
            </View>
          </View>
        )}

        {/* Insights & Recommendations */}
        {summary && (
          <View style={[styles.insightsSection, { backgroundColor: colors.surface }]}>
            <View style={styles.sectionHeader}>
              <View style={[styles.sectionIcon, { backgroundColor: Colors.success + '15' }]}>
                <CustomIcon name="lightbulb" size={20} color={Colors.success} />
              </View>
              <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
                AI Insights
              </Text>
            </View>

            {/* Summary */}
            <View style={[styles.summaryBox, { backgroundColor: Colors.primary + '10' }]}>
              <Text style={[styles.summaryText, { color: colors.textPrimary }]}>
                {summary.daily_summary}
              </Text>
            </View>

            {/* Key Insights */}
            {summary.key_insights && summary.key_insights.length > 0 && (
              <View style={styles.insightsList}>
                <Text style={[styles.insightsSubtitle, { color: colors.textPrimary }]}>
                  Key Insights
                </Text>
                {summary.key_insights.map((insight: string, index: number) => (
                  <View key={index} style={styles.insightRow}>
                    <View style={[styles.insightDot, { backgroundColor: Colors.primary }]} />
                    <Text style={[styles.insightText, { color: colors.textSecondary }]}>
                      {stripEmojis(insight)}
                    </Text>
                  </View>
                ))}
              </View>
            )}

            {/* Natural Remedies Section */}
            {summary.natural_remedies && summary.natural_remedies.length > 0 && (
              <View style={styles.recommendationsList}>
                <View style={styles.recommendationHeader}>
                  <View style={[styles.recommendationHeaderIcon, { backgroundColor: Colors.success + '15' }]}>
                    <CustomIcon name="leaf" size={16} color={Colors.success} />
                  </View>
                  <Text style={[styles.recommendationsSubtitle, { color: colors.textPrimary }]}>
                    Natural Remedies
                  </Text>
                </View>
                {summary.natural_remedies.map((rec: string, index: number) => (
                  <View key={index} style={styles.recommendationRow}>
                    <View style={[styles.recommendationCheck, { backgroundColor: Colors.success + '20' }]}>
                      <CustomIcon name="checkmark" size={12} color={Colors.success} />
                    </View>
                    <Text style={[styles.recommendationText, { color: colors.textSecondary }]}>
                      {stripEmojis(rec)}
                    </Text>
                  </View>
                ))}
              </View>
            )}

            {/* Product Recommendations Section */}
            {summary.product_recommendations && summary.product_recommendations.length > 0 && (
              <View style={styles.recommendationsList}>
                <View style={styles.recommendationHeader}>
                  <View style={[styles.recommendationHeaderIcon, { backgroundColor: Colors.primary + '15' }]}>
                    <CustomIcon name="flask" size={16} color={Colors.primary} />
                  </View>
                  <Text style={[styles.recommendationsSubtitle, { color: colors.textPrimary }]}>
                    Product Recommendations
                  </Text>
                </View>
                {summary.product_recommendations.map((rec: string, index: number) => (
                  <View key={index} style={styles.recommendationRow}>
                    <View style={[styles.recommendationCheck, { backgroundColor: Colors.primary + '20' }]}>
                      <CustomIcon name="checkmark" size={12} color={Colors.primary} />
                    </View>
                    <Text style={[styles.recommendationText, { color: colors.textSecondary }]}>
                      {stripEmojis(rec)}
                    </Text>
                  </View>
                ))}
              </View>
            )}

            {/* Lifestyle Tip Section */}
            {summary.lifestyle_tip && (
              <View style={styles.recommendationsList}>
                <View style={styles.recommendationHeader}>
                  <View style={[styles.recommendationHeaderIcon, { backgroundColor: Colors.accent + '15' }]}>
                    <CustomIcon name="heart" size={16} color={Colors.accent} />
                  </View>
                  <Text style={[styles.recommendationsSubtitle, { color: colors.textPrimary }]}>
                    Lifestyle Tip
                  </Text>
                </View>
                <View style={styles.recommendationRow}>
                  <View style={[styles.recommendationCheck, { backgroundColor: Colors.accent + '20' }]}>
                    <CustomIcon name="checkmark" size={12} color={Colors.accent} />
                  </View>
                  <Text style={[styles.recommendationText, { color: colors.textSecondary }]}>
                    {stripEmojis(summary.lifestyle_tip)}
                  </Text>
                </View>
              </View>
            )}

            {/* Medical Disclaimer */}
            <View style={[styles.disclaimerBox, { backgroundColor: Colors.warning + '10', borderColor: Colors.warning + '30' }]}>
              <View style={styles.disclaimerHeader}>
                <CustomIcon name="alert-triangle" size={18} color={Colors.warning} />
                <Text style={[styles.disclaimerTitle, { color: Colors.warning }]}>
                  Important Notice
                </Text>
              </View>
              <Text style={[styles.disclaimerText, { color: colors.textSecondary }]}>
                These recommendations are AI-generated for informational purposes only and are not a substitute for professional medical advice. 
                Always consult with a dermatologist or healthcare provider before trying new skincare products or treatments. 
                SleepFace is not responsible for any results or reactions from following these suggestions.
              </Text>
            </View>
          </View>
        )}

        {/* Action Buttons */}
        <View style={styles.actionsSection}>
          <TouchableOpacity
            style={styles.shareAction}
            onPress={handleShare}
          >
            <LinearGradient
              colors={[Colors.primary, Colors.accent]}
              style={styles.actionGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
            >
              <CustomIcon name="share" size={20} color="#FFFFFF" />
              <Text style={styles.actionText}>Share Results</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* Guest Prompt */}
        {isGuest && (
          <View style={[styles.guestPrompt, { backgroundColor: colors.surface }]}>
            <LinearGradient
              colors={[Colors.primary + '10', Colors.accent + '10']}
              style={styles.guestPromptGradient}
            >
              <View style={[styles.guestPromptIcon, { backgroundColor: Colors.primary + '20' }]}>
                <CustomIcon name="lock" size={32} color={Colors.primary} />
              </View>
              <Text style={[styles.guestPromptTitle, { color: colors.textPrimary }]}>
                Unlock Full History
              </Text>
              <Text style={[styles.guestPromptText, { color: colors.textSecondary }]}>
                Register to save all your analyses, track progress over time, and get personalized weekly insights
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
            </LinearGradient>
          </View>
        )}
      </Animated.View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
};

// ============================================================================
// STYLES
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
  },
  headerTop: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  headerBackButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  headerDate: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 2,
  },
  headerShareButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    backgroundColor: 'rgba(255,255,255,0.15)',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 20,
    alignSelf: 'center',
  },
  statusBadgeText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  
  // Content
  content: {
    paddingTop: 20,
  },
  
  // Scores Section
  scoresSection: {
    marginHorizontal: 20,
    marginBottom: 16,
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '800',
    marginBottom: 20,
  },
  scoreRingsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  
  // Circular Progress
  circularProgress: {
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  circularProgressBg: {
    position: 'absolute',
  },
  circularProgressFill: {
    position: 'absolute',
  },
  circularProgressContent: {
    alignItems: 'center',
  },
  circularProgressScore: {
    fontSize: 36,
    fontWeight: '800',
  },
  circularProgressLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 4,
  },
  circularProgressStatus: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 2,
  },
  
  // Features Section
  featuresSection: {
    marginHorizontal: 20,
    marginBottom: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 16,
  },
  sectionIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  featuresGrid: {
    gap: 12,
  },
  featureCard: {
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  featureCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  featureCardIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  featureCardInfo: {
    flex: 1,
    marginLeft: 12,
  },
  featureCardName: {
    fontSize: 16,
    fontWeight: '700',
  },
  featureCardStatus: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 2,
  },
  featureCardScore: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  featureCardScoreValue: {
    fontSize: 24,
    fontWeight: '800',
  },
  featureCardScoreMax: {
    fontSize: 14,
    fontWeight: '600',
  },
  featureCardBar: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
  },
  featureCardBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  
  // Routine Section
  routineSection: {
    marginHorizontal: 20,
    marginBottom: 16,
    borderRadius: 24,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  routineGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  routineItem: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    minWidth: '47%',
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  routineItemFull: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  routineIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  routineContent: {
    flex: 1,
  },
  routineLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 2,
  },
  routineValue: {
    fontSize: 16,
    fontWeight: '700',
  },
  
  // Insights Section
  insightsSection: {
    marginHorizontal: 20,
    marginBottom: 16,
    borderRadius: 24,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  summaryBox: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  summaryText: {
    fontSize: 15,
    lineHeight: 22,
    fontWeight: '500',
  },
  insightsList: {
    marginBottom: 20,
  },
  insightsSubtitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 12,
  },
  insightRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: 10,
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
  recommendationsList: {
    marginBottom: 16,
  },
  recommendationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  recommendationHeaderIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  recommendationsSubtitle: {
    fontSize: 16,
    fontWeight: '700',
  },
  recommendationRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: 10,
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
  
  // Disclaimer
  disclaimerBox: {
    marginTop: 20,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
  },
  disclaimerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  disclaimerTitle: {
    fontSize: 14,
    fontWeight: '700',
  },
  disclaimerText: {
    fontSize: 12,
    lineHeight: 18,
    fontStyle: 'italic',
  },
  
  // Actions
  actionsSection: {
    marginHorizontal: 20,
    marginBottom: 16,
  },
  shareAction: {
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  actionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 8,
  },
  actionText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  secondaryAction: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 16,
    gap: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  secondaryActionText: {
    fontSize: 16,
    fontWeight: '700',
  },
  
  // Guest Prompt
  guestPrompt: {
    marginHorizontal: 20,
    borderRadius: 24,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  guestPromptGradient: {
    padding: 32,
    alignItems: 'center',
  },
  guestPromptIcon: {
    width: 72,
    height: 72,
    borderRadius: 36,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  guestPromptTitle: {
    fontSize: 22,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 8,
  },
  guestPromptText: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 24,
  },
  guestPromptCTA: {
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  guestPromptCTAGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    paddingHorizontal: 28,
    gap: 8,
  },
  guestPromptCTAText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  
  // Empty State
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyStateIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  emptyStateTitle: {
    fontSize: 24,
    fontWeight: '800',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyStateText: {
    fontSize: 15,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 32,
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
});

export default AnalysisScreen;

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Animated,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomIcon from '../components/CustomIcon';
import { useAnalysis } from '../contexts/AnalysisContext';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { Colors, Typography, Spacing, BorderRadius, getThemeColors } from '../design/DesignSystem';
import ThemeToggle from '../components/ThemeToggle';
import PrivacyPolicyModal from '../components/PrivacyPolicyModal';
import TermsModal from '../components/TermsModal';
import HelpSupportModal from '../components/HelpSupportModal';
import AboutModal from '../components/AboutModal';

// ============================================================================
// ANIMATED STAT CARD
// ============================================================================
const StatCard: React.FC<{
  icon: string;
  value: number;
  label: string;
  color: string;
  delay?: number;
}> = ({ icon, value, label, color, delay = 0 }) => {
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const scaleAnim = React.useRef(new Animated.Value(0)).current;
  const [animatedValue] = useState(new Animated.Value(0));

  React.useEffect(() => {
    Animated.sequence([
      Animated.delay(delay),
      Animated.parallel([
        Animated.spring(scaleAnim, {
          toValue: 1,
          useNativeDriver: true,
          tension: 50,
          friction: 7,
        }),
        Animated.timing(animatedValue, {
          toValue: value,
          duration: 1000,
          useNativeDriver: false,
        }),
      ]),
    ]).start();
  }, [value]);

  return (
    <Animated.View style={[styles.statCard, { transform: [{ scale: scaleAnim }] }]}>
      <LinearGradient
        colors={[color + '20', color + '10']}
        style={styles.statGradient}
      >
        <View style={[styles.statIconContainer, { backgroundColor: color + '30' }]}>
          <CustomIcon name={icon} size={24} color={color} />
        </View>
        <Text style={[styles.statValue, { color: colors.textPrimary }]}>{value}</Text>
        <Text style={[styles.statLabel, { color: colors.textSecondary }]}>{label}</Text>
      </LinearGradient>
    </Animated.View>
  );
};

// ============================================================================
// ACHIEVEMENT BADGE
// ============================================================================
const AchievementBadge: React.FC<{
  name: string;
  icon: string;
  color: string;
  delay?: number;
}> = ({ name, icon, color, delay = 0 }) => {
  const slideAnim = React.useRef(new Animated.Value(50)).current;
  const opacityAnim = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    Animated.sequence([
      Animated.delay(delay),
      Animated.parallel([
        Animated.spring(slideAnim, {
          toValue: 0,
          useNativeDriver: true,
          tension: 50,
          friction: 7,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
      ]),
    ]).start();
  }, []);

  return (
    <Animated.View
      style={[
        styles.badge,
        {
          transform: [{ translateX: slideAnim }],
          opacity: opacityAnim,
        },
      ]}
    >
      <LinearGradient
        colors={[color, color + 'DD']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.badgeGradient}
      >
        <View style={styles.badgeIcon}>
          <CustomIcon name={icon} size={16} color="#FFFFFF" />
        </View>
        <Text style={styles.badgeText}>{name}</Text>
      </LinearGradient>
    </Animated.View>
  );
};

// ============================================================================
// MAIN PROFILE SCREEN
// ============================================================================
const ProfileScreen: React.FC = () => {
  const { analyses, streakData, resetAllData } = useAnalysis();
  const { user, isGuest, logout, deleteAccount } = useAuth();
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const [showPrivacyPolicy, setShowPrivacyPolicy] = useState(false);
  const [showTerms, setShowTerms] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showAbout, setShowAbout] = useState(false);

  React.useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start();
  }, []);

  const getTotalScans = () => analyses.length;
  const getAverageSleepScore = () => {
    if (analyses.length === 0) return 0;
    const total = analyses.reduce((sum, analysis) => sum + analysis.sleep_score, 0);
    return Math.round(total / analyses.length);
  };
  const getAverageSkinScore = () => {
    if (analyses.length === 0) return 0;
    const total = analyses.reduce((sum, analysis) => sum + analysis.skin_health_score, 0);
    return Math.round(total / analyses.length);
  };

  const getBadges = () => {
    const badges = [];
    if (streakData.current_streak >= 7) {
      badges.push({ name: 'Week Warrior', icon: 'trophy', color: '#F59E0B' });
    }
    if (streakData.current_streak >= 30) {
      badges.push({ name: 'Month Master', icon: 'award', color: '#8B5CF6' });
    }
    if (getAverageSleepScore() >= 80) {
      badges.push({ name: 'Sleep Champion', icon: 'moon', color: '#3B82F6' });
    }
    if (getTotalScans() >= 50) {
      badges.push({ name: 'Dedicated Tracker', icon: 'target', color: '#10B981' });
    }
    return badges;
  };

  const badges = getBadges();

  const handleLogout = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Sign Out', 
          style: 'destructive',
          onPress: logout
        }
      ]
    );
  };

  const handleResetData = () => {
    Alert.alert(
      'Delete Account',
      'This will permanently delete all your analysis data. This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Reset', 
          style: 'destructive',
          onPress: resetAllData
        }
      ]
    );
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      'Delete Account',
      'This will permanently delete your account and ALL data. This action cannot be undone.\n\nAre you absolutely sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete Forever', 
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteAccount();
              Alert.alert('Account Deleted', 'Your account and all data have been permanently deleted.');
            } catch (error: any) {
              Alert.alert('Error', error?.message || 'Failed to delete account. Please try again.');
            }
          }
        }
      ]
    );
  };

  return (
    <ScrollView 
      style={[styles.container, { backgroundColor: colors.background }]}
      showsVerticalScrollIndicator={false}
    >
      {/* Premium Header with Gradient */}
      <LinearGradient
        colors={[Colors.primary, Colors.accent]}
        style={styles.header}
      >
        {/* Theme Toggle */}
        <View style={styles.themeToggle}>
          <ThemeToggle size={20} />
        </View>

        {/* Profile Section */}
        <Animated.View style={[styles.profileSection, { opacity: fadeAnim }]}>
          <View style={styles.avatarContainer}>
            <LinearGradient
              colors={['rgba(255,255,255,0.3)', 'rgba(255,255,255,0.1)']}
              style={styles.avatarGradient}
            >
              <CustomIcon name="user" size={56} color="#FFFFFF" />
            </LinearGradient>
            <View style={styles.statusDot} />
          </View>

          <Text style={styles.userName}>
            {user ? user.displayName : (isGuest ? 'Guest User' : 'Sleep Tracker')}
          </Text>
          
          <Text style={styles.userEmail}>
            {user ? user.email : (isGuest ? 'Tap to register for full features' : 'Track your wellness journey')}
          </Text>

          {isGuest && (
            <TouchableOpacity style={styles.upgradeButton}>
              <LinearGradient
                colors={['rgba(255,255,255,0.25)', 'rgba(255,255,255,0.15)']}
                style={styles.upgradeGradient}
              >
                <CustomIcon name="sparkles" size={16} color="#FFFFFF" />
                <Text style={styles.upgradeText}>Upgrade Account</Text>
              </LinearGradient>
            </TouchableOpacity>
          )}
        </Animated.View>
      </LinearGradient>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <StatCard
          icon="fire"
          value={streakData.current_streak}
          label="Day Streak"
          color="#FF6B35"
          delay={0}
        />
        <StatCard
          icon="camera"
          value={getTotalScans()}
          label="Total Scans"
          color="#6366F1"
          delay={100}
        />
        <StatCard
          icon="moon"
          value={getAverageSleepScore()}
          label="Avg Sleep"
          color="#3B82F6"
          delay={200}
        />
        <StatCard
          icon="sparkles"
          value={getAverageSkinScore()}
          label="Avg Skin"
          color="#10B981"
          delay={300}
        />
      </View>

      {/* Achievements */}
      {badges.length > 0 && (
        <View style={[styles.section, { backgroundColor: colors.surface }]}>
          <View style={styles.sectionHeader}>
            <View style={styles.sectionTitleRow}>
              <View style={[styles.sectionIcon, { backgroundColor: Colors.accent + '20' }]}>
                <CustomIcon name="trophy" size={20} color={Colors.accent} />
              </View>
              <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
                Achievements
              </Text>
            </View>
            <View style={styles.badgeCount}>
              <Text style={styles.badgeCountText}>{badges.length}</Text>
            </View>
          </View>

          <View style={styles.badgesGrid}>
            {badges.map((badge, index) => (
              <AchievementBadge
                key={index}
                name={badge.name}
                icon={badge.icon}
                color={badge.color}
                delay={index * 100}
              />
            ))}
          </View>
        </View>
      )}

      {/* Account Section */}
      <View style={[styles.section, { backgroundColor: colors.surface }]}>
        <View style={styles.sectionHeader}>
          <View style={styles.sectionTitleRow}>
            <View style={[styles.sectionIcon, { backgroundColor: Colors.primary + '20' }]}>
              <CustomIcon name="user" size={20} color={Colors.primary} />
            </View>
            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              Account
            </Text>
          </View>
        </View>

        <View style={styles.menuList}>
          {!user && (
            <>
              <TouchableOpacity style={styles.menuItem}>
                <View style={styles.menuLeft}>
                  <View style={[styles.menuIcon, { backgroundColor: Colors.primary + '15' }]}>
                    <CustomIcon name="log-in" size={20} color={Colors.primary} />
                  </View>
                  <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                    Sign In
                  </Text>
                </View>
                <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
              </TouchableOpacity>

              <View style={[styles.menuDivider, { backgroundColor: colors.border }]} />

              <TouchableOpacity style={styles.menuItem}>
                <View style={styles.menuLeft}>
                  <View style={[styles.menuIcon, { backgroundColor: Colors.accent + '15' }]}>
                    <CustomIcon name="user-plus" size={20} color={Colors.accent} />
                  </View>
                  <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                    Create Account
                  </Text>
                </View>
                <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
              </TouchableOpacity>
            </>
          )}

          {isGuest && (
            <TouchableOpacity style={styles.menuItem}>
              <View style={styles.menuLeft}>
                <View style={[styles.menuIcon, { backgroundColor: Colors.primary + '15' }]}>
                  <CustomIcon name="sparkles" size={20} color={Colors.primary} />
                </View>
                <View style={styles.menuTextContainer}>
                  <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                    Register for Full Features
                  </Text>
                  <Text style={[styles.menuSubtext, { color: colors.textTertiary }]}>
                    Save history, track trends, get insights
                  </Text>
                </View>
              </View>
              <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
            </TouchableOpacity>
          )}

          {user && (
            <>
              <TouchableOpacity style={styles.menuItem}>
                <View style={styles.menuLeft}>
                  <View style={[styles.menuIcon, { backgroundColor: Colors.primary + '15' }]}>
                    <CustomIcon name="edit" size={20} color={Colors.primary} />
                  </View>
                  <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                    Edit Profile
                  </Text>
                </View>
                <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
              </TouchableOpacity>

              <View style={[styles.menuDivider, { backgroundColor: colors.border }]} />

              <TouchableOpacity style={styles.menuItem} onPress={handleLogout}>
                <View style={styles.menuLeft}>
                  <View style={[styles.menuIcon, { backgroundColor: Colors.error + '15' }]}>
                    <CustomIcon name="log-out" size={20} color={Colors.error} />
                  </View>
                  <Text style={[styles.menuText, { color: Colors.error }]}>
                    Sign Out
                  </Text>
                </View>
                <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>

      {/* Settings Section */}
      <View style={[styles.section, { backgroundColor: colors.surface }]}>
        <View style={styles.sectionHeader}>
          <View style={styles.sectionTitleRow}>
            <View style={[styles.sectionIcon, { backgroundColor: '#8B5CF6' + '20' }]}>
              <CustomIcon name="settings" size={20} color="#8B5CF6" />
            </View>
            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              Settings
            </Text>
          </View>
        </View>

        <View style={styles.menuList}>
          <TouchableOpacity style={styles.menuItem}>
            <View style={styles.menuLeft}>
              <View style={[styles.menuIcon, { backgroundColor: '#8B5CF6' + '15' }]}>
                <CustomIcon name="bell" size={20} color="#8B5CF6" />
              </View>
              <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                Notifications
              </Text>
            </View>
            <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
          </TouchableOpacity>

          <View style={[styles.menuDivider, { backgroundColor: colors.border }]} />

          <TouchableOpacity style={styles.menuItem} onPress={() => setShowPrivacyPolicy(true)}>
            <View style={styles.menuLeft}>
              <View style={[styles.menuIcon, { backgroundColor: "#8B5CF6" + "15" }]}>
                <CustomIcon name="lock" size={20} color="#8B5CF6" />
              </View>
              <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                Privacy & Security
              </Text>
            </View>
            <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
          </TouchableOpacity>

          <View style={[styles.menuDivider, { backgroundColor: colors.border }]} />

          <TouchableOpacity style={styles.menuItem} onPress={() => setShowTerms(true)}>
            <View style={styles.menuLeft}>
              <View style={[styles.menuIcon, { backgroundColor: "#8B5CF6" + "15" }]}>
                <CustomIcon name="database" size={20} color="#8B5CF6" />
              </View>
              <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                Terms & Conditions
              </Text>
            </View>
            <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Support Section */}
      <View style={[styles.section, { backgroundColor: colors.surface }]}>
        <View style={styles.sectionHeader}>
          <View style={styles.sectionTitleRow}>
            <View style={[styles.sectionIcon, { backgroundColor: '#10B981' + '20' }]}>
              <CustomIcon name="help-circle" size={20} color="#10B981" />
            </View>
            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              Support
            </Text>
          </View>
        </View>

        <View style={styles.menuList}>
          <TouchableOpacity style={styles.menuItem} onPress={() => setShowHelp(true)}>
            <View style={styles.menuLeft}>
              <View style={[styles.menuIcon, { backgroundColor: '#10B981' + '15' }]}>
                <CustomIcon name="help-circle" size={20} color="#10B981" />
              </View>
              <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                Help & Support
              </Text>
            </View>
            <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
          </TouchableOpacity>

          <View style={[styles.menuDivider, { backgroundColor: colors.border }]} />

          <TouchableOpacity style={styles.menuItem}>
            <View style={styles.menuLeft}>
              <View style={[styles.menuIcon, { backgroundColor: '#10B981' + '15' }]}>
                <CustomIcon name="star" size={20} color="#10B981" />
              </View>
              <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                Rate App
              </Text>
            </View>
            <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
          </TouchableOpacity>

          <View style={[styles.menuDivider, { backgroundColor: colors.border }]} />

          <TouchableOpacity style={styles.menuItem} onPress={() => setShowAbout(true)}>
            <View style={styles.menuLeft}>
              <View style={[styles.menuIcon, { backgroundColor: "#10B981" + "15" }]}>
                <CustomIcon name="info" size={20} color="#10B981" />
              </View>
              <Text style={[styles.menuText, { color: colors.textPrimary }]}>
                About
              </Text>
            </View>
            <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Danger Zone */}
      <View style={[styles.section, { backgroundColor: colors.surface }]}>
        <View style={styles.sectionHeader}>
          <View style={styles.sectionTitleRow}>
            <View style={[styles.sectionIcon, { backgroundColor: Colors.error + '20' }]}>
              <CustomIcon name="alert-triangle" size={20} color={Colors.error} />
            </View>
            <Text style={[styles.sectionTitle, { color: Colors.error }]}>
              Danger Zone
            </Text>
          </View>
        </View>

        <View style={styles.menuList}>
          <TouchableOpacity style={styles.menuItem} onPress={handleDeleteAccount}>
            <View style={styles.menuLeft}>
              <View style={[styles.menuIcon, { backgroundColor: Colors.error + '15' }]}>
                <CustomIcon name="trash-2" size={20} color={Colors.error} />
              </View>
              <View style={styles.menuTextContainer}>
                <Text style={[styles.menuText, { color: Colors.error }]}>
                  Delete Account
                </Text>
                <Text style={[styles.menuSubtext, { color: Colors.error + 'CC' }]}>
                  Permanently delete account and all data
                </Text>
              </View>
            </View>
            <CustomIcon name="chevronRight" size={20} color={Colors.error} />
          </TouchableOpacity>
        </View>
      </View>

      {/* App Version */}
      <Text style={[styles.appVersion, { color: colors.textTertiary }]}>
        Version 1.0.0
      </Text>

      <View style={{ height: 100 }} />

      {/* Modals */}
      <PrivacyPolicyModal
        visible={showPrivacyPolicy}
        onClose={() => setShowPrivacyPolicy(false)}
      />
      <TermsModal
        visible={showTerms}
        onClose={() => setShowTerms(false)}
      />
      <HelpSupportModal
        visible={showHelp}
        onClose={() => setShowHelp(false)}
      />
      <AboutModal
        visible={showAbout}
        onClose={() => setShowAbout(false)}
      />
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
  
  // Header
  header: {
    paddingTop: 60,
    paddingBottom: 40,
    paddingHorizontal: 20,
  },
  themeToggle: {
    position: 'absolute',
    top: 60,
    right: 20,
    zIndex: 1,
  },
  profileSection: {
    alignItems: 'center',
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  avatarGradient: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: 'rgba(255,255,255,0.3)',
  },
  statusDot: {
    position: 'absolute',
    bottom: 4,
    right: 4,
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#10B981',
    borderWidth: 3,
    borderColor: '#FFFFFF',
  },
  userName: {
    fontSize: 24,
    fontWeight: '800',
    // color: '#FFFFFF', -- removed for theme support
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    // color: 'rgba(255,255,255,0.8)', -- removed for theme support
    textAlign: 'center',
    marginBottom: 16,
  },
  upgradeButton: {
    borderRadius: 20,
    overflow: 'hidden',
    marginTop: 8,
  },
  upgradeGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    paddingHorizontal: 20,
    gap: 6,
  },
  upgradeText: {
    fontSize: 14,
    fontWeight: '700',
    // color: '#FFFFFF', -- removed for theme support
  },
  
  // Stats
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 20,
    marginTop: 20,
    marginBottom: 20,
    gap: 12,
  },
  statCard: {
    width: '48%',
    borderRadius: 16,
    overflow: 'hidden',
  },
  statGradient: {
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  statIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  statValue: {
    fontSize: 28,
    fontWeight: '800',
    // color: '#FFFFFF', -- removed for theme support
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    // color: 'rgba(255,255,255,0.8)', -- removed for theme support
    fontWeight: '600',
  },
  
  // Sections
  section: {
    marginHorizontal: 20,
    marginBottom: 16,
    borderRadius: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  sectionIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  
  // Badges
  badgeCount: {
    backgroundColor: Colors.accent + '20',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeCountText: {
    fontSize: 12,
    fontWeight: '700',
    color: Colors.accent,
  },
  badgesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  badge: {
    borderRadius: 20,
    overflow: 'hidden',
  },
  badgeGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    gap: 6,
  },
  badgeIcon: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '700',
    // color: '#FFFFFF', -- removed for theme support
  },
  
  // Menu
  menuList: {
    gap: 0,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
  },
  menuLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: 12,
  },
  menuIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  menuTextContainer: {
    flex: 1,
  },
  menuText: {
    fontSize: 15,
    fontWeight: '600',
  },
  menuSubtext: {
    fontSize: 12,
    marginTop: 2,
  },
  menuDivider: {
    height: 1,
    marginLeft: 52,
  },
  
  // Footer
  appVersion: {
    textAlign: 'center',
    fontSize: 12,
    marginTop: 20,
  },
});

export default ProfileScreen;

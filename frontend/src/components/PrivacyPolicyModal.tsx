import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomIcon from './CustomIcon';
import { Colors, getThemeColors } from '../design/DesignSystem';
import { useTheme } from '../contexts/ThemeContext';

interface PrivacyPolicyModalProps {
  visible: boolean;
  onClose: () => void;
}

const PrivacyPolicyModal: React.FC<PrivacyPolicyModalProps> = ({ visible, onClose }) => {
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={[styles.modalContainer, { backgroundColor: colors.surface }]}>
          {/* Header */}
          <LinearGradient
            colors={[Colors.primary, Colors.accent]}
            style={styles.header}
          >
            <Text style={styles.headerTitle}>Privacy Policy</Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <CustomIcon name="close" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </LinearGradient>

          {/* Content */}
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            <Text style={[styles.lastUpdated, { color: colors.textTertiary }]}>
              Last updated: October 18, 2025
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              1. Information We Collect
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              SleepFace collects and processes the following information:
              {'\n\n'}
              • <Text style={{ fontWeight: '600' }}>Face Images</Text>: Analyzed for sleep and skin health indicators. Images are processed and then deleted - we do not permanently store your photos.
              {'\n\n'}
              • <Text style={{ fontWeight: '600' }}>Routine Data</Text>: Sleep hours, water intake, and skincare products you choose to log.
              {'\n\n'}
              • <Text style={{ fontWeight: '600' }}>Analysis Results</Text>: Sleep scores, skin health scores, and feature measurements.
              {'\n\n'}
              • <Text style={{ fontWeight: '600' }}>Account Information</Text>: Email and display name (for registered users only).
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              2. How We Use Your Information
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              We use your information to:
              {'\n\n'}
              • Provide AI-powered sleep and skin health analysis
              {'\n\n'}
              • Generate personalized recommendations
              {'\n\n'}
              • Track your progress over time
              {'\n\n'}
              • Improve our AI models and service quality
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              3. Biometric Data Notice
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              <Text style={{ fontWeight: '700', color: Colors.warning }}>Important:</Text> SleepFace processes face images to analyze sleep quality and skin health. This constitutes biometric data in some jurisdictions.
              {'\n\n'}
              • Your face images are <Text style={{ fontWeight: '600' }}>processed on our servers</Text> for analysis
              {'\n\n'}
              • Images are <Text style={{ fontWeight: '600' }}>automatically deleted</Text> after analysis
              {'\n\n'}
              • We <Text style={{ fontWeight: '600' }}>do not store</Text> raw face images
              {'\n\n'}
              • We <Text style={{ fontWeight: '600' }}>do not share</Text> your images with third parties
              {'\n\n'}
              • Analysis results (scores, features) are saved to track your progress
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              4. Third-Party Services
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              We use the following third-party services:
              {'\n\n'}
              • <Text style={{ fontWeight: '600' }}>OpenAI API</Text>: For generating personalized skincare recommendations. Analysis data (scores, features) is sent anonymously without your personal information.
              {'\n\n'}
              • <Text style={{ fontWeight: '600' }}>MongoDB Atlas</Text>: For secure, encrypted data storage.
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              5. Data Retention
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              • <Text style={{ fontWeight: '600' }}>Registered Users</Text>: Your analysis data is kept as long as your account is active.
              {'\n\n'}
              • <Text style={{ fontWeight: '600' }}>Guest Users</Text>: Data is stored locally on your device only and not synced to our servers.
              {'\n\n'}
              • <Text style={{ fontWeight: '600' }}>Account Deletion</Text>: All your data is permanently deleted within 30 days of account deletion.
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              6. Your Rights
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              You have the right to:
              {'\n\n'}
              • Access your data
              {'\n\n'}
              • Delete your account and all associated data
              {'\n\n'}
              • Opt-out of AI-powered recommendations
              {'\n\n'}
              • Contact us with privacy concerns
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              7. Children's Privacy
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              SleepFace is not intended for users under 13 years of age. We do not knowingly collect data from children.
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              8. Contact Us
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              For privacy-related questions or to exercise your rights, contact us at:
              {'\n\n'}
              <Text style={{ fontWeight: '600', color: Colors.primary }}>support@sleepface.app</Text>
            </Text>

            <View style={{ height: 40 }} />
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'flex-end',
  },
  modalContainer: {
    height: '90%',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    overflow: 'hidden',
  },
  header: {
    paddingTop: 20,
    paddingBottom: 20,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  closeButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  lastUpdated: {
    fontSize: 12,
    marginBottom: 20,
    fontStyle: 'italic',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginTop: 20,
    marginBottom: 12,
  },
  paragraph: {
    fontSize: 14,
    lineHeight: 22,
  },
});

export default PrivacyPolicyModal;


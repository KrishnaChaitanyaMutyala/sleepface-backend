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

interface TermsModalProps {
  visible: boolean;
  onClose: () => void;
}

const TermsModal: React.FC<TermsModalProps> = ({ visible, onClose }) => {
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
            <Text style={styles.headerTitle}>Terms of Service</Text>
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
              1. Acceptance of Terms
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              By using SleepFace, you agree to these Terms of Service. If you do not agree, please do not use the app.
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              2. Service Description
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              SleepFace provides AI-powered analysis of sleep quality and skin health based on selfie images. The service includes:
              {'\n\n'}
              • Facial feature analysis for sleep and skin indicators
              {'\n\n'}
              • Personalized recommendations
              {'\n\n'}
              • Progress tracking over time
              {'\n\n'}
              • Routine logging (sleep, water, skincare products)
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              3. Medical Disclaimer
            </Text>
            <Text style={[styles.paragraph, { color: Colors.warning }]}>
              <Text style={{ fontWeight: '700' }}>IMPORTANT:</Text> SleepFace is NOT a medical device and does not provide medical advice, diagnosis, or treatment.
              {'\n\n'}
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              • Our AI analysis is for <Text style={{ fontWeight: '600' }}>informational and educational purposes only</Text>
              {'\n\n'}
              • Recommendations are <Text style={{ fontWeight: '600' }}>not a substitute for professional medical advice</Text>
              {'\n\n'}
              • Always <Text style={{ fontWeight: '600' }}>consult a qualified healthcare provider</Text> before trying new skincare products or treatments
              {'\n\n'}
              • We are <Text style={{ fontWeight: '600' }}>not responsible</Text> for any results or reactions from following our recommendations
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              4. User Responsibilities
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              You agree to:
              {'\n\n'}
              • Provide accurate information when creating your account
              {'\n\n'}
              • Keep your account credentials secure
              {'\n\n'}
              • Use the app for personal, non-commercial purposes only
              {'\n\n'}
              • Not attempt to reverse engineer or manipulate the AI
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              5. Data Usage & Consent
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              By using SleepFace, you consent to:
              {'\n\n'}
              • Processing of your face images for analysis (images are deleted after processing)
              {'\n\n'}
              • Storage of analysis results and routine data
              {'\n\n'}
              • Use of your data to improve AI models (anonymized)
              {'\n\n'}
              • Sharing analysis data with OpenAI API for recommendations (anonymized)
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              6. Intellectual Property
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              All content, features, and functionality of SleepFace are owned by us and protected by copyright, trademark, and other laws.
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              7. Limitation of Liability
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              SleepFace is provided "as is" without warranties. We are not liable for:
              {'\n\n'}
              • Accuracy of AI analysis or recommendations
              {'\n\n'}
              • Any health outcomes from using the app
              {'\n\n'}
              • Skin reactions to recommended products
              {'\n\n'}
              • Data loss or service interruptions
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              8. Account Termination
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              You may delete your account at any time through Profile → Danger Zone → Delete Account. Upon deletion, all your data will be permanently removed within 30 days.
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              9. Changes to Terms
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              We may update these Terms from time to time. Continued use of the app after changes constitutes acceptance of new terms.
            </Text>

            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              10. Contact
            </Text>
            <Text style={[styles.paragraph, { color: colors.textSecondary }]}>
              For questions about these Terms, contact:
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

export default TermsModal;


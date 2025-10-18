import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  ScrollView,
  TouchableOpacity,
  Linking,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomIcon from './CustomIcon';
import { Colors, getThemeColors } from '../design/DesignSystem';
import { useTheme } from '../contexts/ThemeContext';

interface HelpSupportModalProps {
  visible: boolean;
  onClose: () => void;
}

const HelpSupportModal: React.FC<HelpSupportModalProps> = ({ visible, onClose }) => {
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);

  const handleEmailSupport = () => {
    Linking.openURL('mailto:support@sleepface.app?subject=SleepFace Support Request');
  };

  const handleReportBug = () => {
    Linking.openURL('mailto:support@sleepface.app?subject=Bug Report - SleepFace');
  };

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
            colors={[Colors.success, Colors.primary]}
            style={styles.header}
          >
            <Text style={styles.headerTitle}>Help & Support</Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <CustomIcon name="close" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </LinearGradient>

          {/* Content */}
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            {/* FAQ Section */}
            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              Frequently Asked Questions
            </Text>

            <View style={[styles.faqCard, { backgroundColor: colors.surfaceSecondary }]}>
              <Text style={[styles.faqQuestion, { color: colors.textPrimary }]}>
                Q: How accurate is the AI analysis?
              </Text>
              <Text style={[styles.faqAnswer, { color: colors.textSecondary }]}>
                A: Our AI analyzes facial features for sleep and skin indicators. While highly advanced, it's for informational purposes only and not a medical diagnosis. Accuracy improves with consistent daily selfies in good lighting.
              </Text>
            </View>

            <View style={[styles.faqCard, { backgroundColor: colors.surfaceSecondary }]}>
              <Text style={[styles.faqQuestion, { color: colors.textPrimary }]}>
                Q: Are my photos stored?
              </Text>
              <Text style={[styles.faqAnswer, { color: colors.textSecondary }]}>
                A: No. Your face images are processed for analysis and then immediately deleted. We only save the analysis results (scores, features), not your actual photos.
              </Text>
            </View>

            <View style={[styles.faqCard, { backgroundColor: colors.surfaceSecondary }]}>
              <Text style={[styles.faqQuestion, { color: colors.textPrimary }]}>
                Q: Can I use SleepFace without an account?
              </Text>
              <Text style={[styles.faqAnswer, { color: colors.textSecondary }]}>
                A: Yes! Guest mode lets you try the app without registration. However, your data won't be saved and you won't have access to trends and history features.
              </Text>
            </View>

            <View style={[styles.faqCard, { backgroundColor: colors.surfaceSecondary }]}>
              <Text style={[styles.faqQuestion, { color: colors.textPrimary }]}>
                Q: How do I get the best results?
              </Text>
              <Text style={[styles.faqAnswer, { color: colors.textSecondary }]}>
                A: Take selfies in good, natural lighting facing the camera directly. Remove makeup if possible. Take photos at the same time each day for consistent tracking.
              </Text>
            </View>

            {/* Contact Options */}
            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              Contact Us
            </Text>

            <TouchableOpacity
              style={[styles.contactButton, { backgroundColor: Colors.primary + '15', borderColor: Colors.primary + '30' }]}
              onPress={handleEmailSupport}
            >
              <View style={[styles.contactIcon, { backgroundColor: Colors.primary + '20' }]}>
                <CustomIcon name="mail" size={20} color={Colors.primary} />
              </View>
              <View style={styles.contactInfo}>
                <Text style={[styles.contactTitle, { color: colors.textPrimary }]}>
                  Email Support
                </Text>
                <Text style={[styles.contactSubtitle, { color: colors.textSecondary }]}>
                  support@sleepface.app
                </Text>
              </View>
              <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.contactButton, { backgroundColor: Colors.error + '15', borderColor: Colors.error + '30' }]}
              onPress={handleReportBug}
            >
              <View style={[styles.contactIcon, { backgroundColor: Colors.error + '20' }]}>
                <CustomIcon name="alert-triangle" size={20} color={Colors.error} />
              </View>
              <View style={styles.contactInfo}>
                <Text style={[styles.contactTitle, { color: colors.textPrimary }]}>
                  Report a Bug
                </Text>
                <Text style={[styles.contactSubtitle, { color: colors.textSecondary }]}>
                  Help us improve the app
                </Text>
              </View>
              <CustomIcon name="chevronRight" size={20} color={colors.textTertiary} />
            </TouchableOpacity>

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
    height: '85%',
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
    marginBottom: 16,
  },
  paragraph: {
    fontSize: 14,
    lineHeight: 22,
  },
  faqCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  faqQuestion: {
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 8,
  },
  faqAnswer: {
    fontSize: 14,
    lineHeight: 20,
  },
  contactButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    marginBottom: 12,
    borderWidth: 1,
  },
  contactIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  contactInfo: {
    flex: 1,
  },
  contactTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 2,
  },
  contactSubtitle: {
    fontSize: 13,
  },
});

export default HelpSupportModal;


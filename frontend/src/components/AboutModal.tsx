import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  ScrollView,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomIcon from './CustomIcon';
import { Colors, getThemeColors } from '../design/DesignSystem';
import { useTheme } from '../contexts/ThemeContext';

interface AboutModalProps {
  visible: boolean;
  onClose: () => void;
}

const AboutModal: React.FC<AboutModalProps> = ({ visible, onClose }) => {
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);

  return (
    <Modal
      visible={visible}
      animationType="fade"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={[styles.modalContainer, { backgroundColor: colors.surface }]}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <CustomIcon name="close" size={24} color={colors.textSecondary} />
          </TouchableOpacity>

          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            {/* Logo */}
            <View style={styles.logoContainer}>
              <LinearGradient
                colors={[Colors.primary, Colors.accent]}
                style={styles.logo}
              >
                <CustomIcon name="sparkles" size={40} color="#FFFFFF" />
              </LinearGradient>
            </View>

            {/* App Name & Version */}
            <Text style={[styles.appName, { color: colors.textPrimary }]}>
              SleepFace
            </Text>
            <Text style={[styles.version, { color: colors.textTertiary }]}>
              Version 1.0.0
            </Text>

            {/* Description */}
            <Text style={[styles.description, { color: colors.textSecondary }]}>
              Track your sleep quality and skin health with AI-powered facial analysis. 
              Get personalized insights and recommendations for better wellness.
            </Text>

            <View style={[styles.divider, { backgroundColor: colors.border }]} />

            {/* AI Disclosure */}
            <View style={[styles.disclosureBox, { backgroundColor: Colors.primary + '10', borderColor: Colors.primary + '30' }]}>
              <View style={styles.disclosureHeader}>
                <CustomIcon name="sparkles" size={20} color={Colors.primary} />
                <Text style={[styles.disclosureTitle, { color: Colors.primary }]}>
                  Powered by AI
                </Text>
              </View>
              <Text style={[styles.disclosureText, { color: colors.textSecondary }]}>
                SleepFace uses advanced artificial intelligence:
                {'\n\n'}
                • <Text style={{ fontWeight: '600' }}>Local TensorFlow Lite</Text> models for real-time facial feature analysis
                {'\n\n'}
                • <Text style={{ fontWeight: '600' }}>OpenAI GPT</Text> for personalized skincare recommendations
                {'\n\n'}
                AI-generated advice is for informational purposes only and not medical guidance.
              </Text>
            </View>

            <View style={[styles.divider, { backgroundColor: colors.border }]} />

            {/* Credits */}
            <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>
              Built With
            </Text>
            <Text style={[styles.creditsText, { color: colors.textSecondary }]}>
              • React Native & Expo
              {'\n'}• TensorFlow Lite
              {'\n'}• OpenAI API
              {'\n'}• MongoDB
              {'\n'}• FastAPI
            </Text>

            {/* Contact */}
            <View style={[styles.divider, { backgroundColor: colors.border }]} />
            
            <Text style={[styles.madeWith, { color: colors.textTertiary }]}>
              Made with ❤️ for your wellness journey
            </Text>

            <TouchableOpacity
              style={[styles.contactButton, { backgroundColor: Colors.primary + '15' }]}
              onPress={() => Linking.openURL('mailto:support@sleepface.app')}
            >
              <CustomIcon name="mail" size={18} color={Colors.primary} />
              <Text style={[styles.contactText, { color: Colors.primary }]}>
                support@sleepface.app
              </Text>
            </TouchableOpacity>

            {/* Copyright */}
            <Text style={[styles.copyright, { color: colors.textTertiary }]}>
              © 2025 SleepFace. All rights reserved.
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
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContainer: {
    width: '100%',
    maxWidth: 420,
    maxHeight: '85%',
    borderRadius: 24,
    overflow: 'hidden',
  },
  closeButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(0,0,0,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
  },
  logoContainer: {
    alignItems: 'center',
    marginTop: 40,
    marginBottom: 20,
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  appName: {
    fontSize: 28,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 4,
  },
  version: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 20,
  },
  description: {
    fontSize: 15,
    lineHeight: 22,
    textAlign: 'center',
    marginBottom: 24,
  },
  divider: {
    height: 1,
    marginVertical: 24,
  },
  disclosureBox: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 8,
  },
  disclosureHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 10,
  },
  disclosureTitle: {
    fontSize: 16,
    fontWeight: '700',
  },
  disclosureText: {
    fontSize: 13,
    lineHeight: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 12,
  },
  creditsText: {
    fontSize: 14,
    lineHeight: 24,
  },
  madeWith: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 16,
  },
  contactButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 12,
    marginBottom: 20,
  },
  contactText: {
    fontSize: 15,
    fontWeight: '600',
  },
  copyright: {
    fontSize: 12,
    textAlign: 'center',
  },
});

export default AboutModal;


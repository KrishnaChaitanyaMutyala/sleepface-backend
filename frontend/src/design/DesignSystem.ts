/**
 * SleepFace Design System
 * Apple-inspired design system with custom icons and robust styling
 */

export const Colors = {
  // Primary Colors
  primary: '#007AFF',      // iOS Blue (ORIGINAL)
  primaryDark: '#0056CC',
  primaryLight: '#4DA6FF',
  
  // Secondary Colors
  secondary: '#5856D6',    // iOS Purple (ORIGINAL)
  secondaryDark: '#3A39A3',
  secondaryLight: '#7B7AE5',
  
  // Accent Colors
  accent: '#FF9500',       // iOS Orange (ORIGINAL)
  accentDark: '#CC7700',
  accentLight: '#FFB84D',
  
  // Success Colors
  success: '#34C759',      // iOS Green (ORIGINAL)
  successDark: '#2AA44A',
  successLight: '#5DD679',
  
  // Warning Colors
  warning: '#FF9500',      // iOS Orange (ORIGINAL)
  warningDark: '#CC7700',
  warningLight: '#FFB84D',
  
  // Error Colors
  error: '#FF3B30',        // iOS Red (ORIGINAL)
  errorDark: '#CC2E26',
  errorLight: '#FF6B61',
  
  // Dark Theme Colors - Apple's actual dark mode
  dark: {
    // Background Colors - Apple's sophisticated dark grays
    background: '#1C1C1E', // iOS Dark Background (not pure black)
    surface: '#2C2C2E', // iOS Dark Surface
    surfaceSecondary: '#3A3A3C', // iOS Dark Surface Secondary
    surfaceTertiary: '#48484A', // iOS Dark Surface Tertiary
    
    // Text Colors - Apple's refined text hierarchy
    textPrimary: '#FFFFFF', // Pure white for primary text
    textSecondary: '#EBEBF5', // iOS Dark Text Secondary (slightly off-white)
    textTertiary: '#EBEBF599', // iOS Dark Text Tertiary (60% opacity)
    textInverse: '#1C1C1E', // Dark background for contrast
    
    // Border Colors - Subtle and refined
    border: '#48484A', // iOS Dark Border
    borderLight: '#3A3A3C', // iOS Dark Border Light
    borderDark: '#636366', // iOS Dark Border Dark
    
    // Shadow Colors - More sophisticated
    shadow: 'rgba(0, 0, 0, 0.4)',
    shadowDark: 'rgba(0, 0, 0, 0.6)',
    shadowLight: 'rgba(0, 0, 0, 0.2)',
  },
  
  // Light Theme Colors (for reference)
  light: {
    // Background Colors
    background: '#F2F2F7', // iOS Background
    surface: '#FFFFFF',
    surfaceSecondary: '#F8F9FA',
    surfaceTertiary: '#F2F2F7',
    
    // Text Colors
    textPrimary: '#1D1D1F',
    textSecondary: '#6D6D70',
    textTertiary: '#8E8E93',
    textInverse: '#FFFFFF',
    
    // Border Colors
    border: '#C6C6C8',
    borderLight: '#E5E5EA',
    borderDark: '#AEAEB2',
    
    // Shadow Colors
    shadow: 'rgba(0, 0, 0, 0.1)',
    shadowDark: 'rgba(0, 0, 0, 0.2)',
    shadowLight: 'rgba(0, 0, 0, 0.05)',
  },
  
  // Default to Dark Theme - Apple's actual dark mode
  background: '#1C1C1E',
  surface: '#2C2C2E',
  surfaceSecondary: '#3A3A3C',
  surfaceTertiary: '#48484A',
  textPrimary: '#FFFFFF',
  textSecondary: '#EBEBF5',
  textTertiary: '#EBEBF599',
  textInverse: '#1C1C1E',
  border: '#48484A',
  borderLight: '#3A3A3C',
  borderDark: '#636366',
  shadow: 'rgba(0, 0, 0, 0.4)',
  shadowDark: 'rgba(0, 0, 0, 0.6)',
  shadowLight: 'rgba(0, 0, 0, 0.2)',
  
  // Feature Colors (bright versions)
  sleepBlue: '#3B82F6',    // Bright Blue - sleep theme
  waterTeal: '#14B8A6',    // Bright Teal - hydration
  fireOrange: '#FF6B35',   // Bright Orange - energy/streak
};

export const Typography = {
  // Font Families
  fontFamily: {
    primary: 'SF Pro Display',
    secondary: 'SF Pro Text',
    mono: 'SF Mono',
  },
  
  // Font Sizes
  fontSize: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 28,
    '4xl': 32,
    '5xl': 36,
    '6xl': 48,
  },
  
  // Font Weights
  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    heavy: '800',
  },
  
  // Line Heights
  lineHeight: {
    tight: 1.2,
    normal: 1.4,
    relaxed: 1.6,
    loose: 1.8,
  },
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
  '4xl': 96,
};

export const BorderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 20,
  '3xl': 24,
  full: 9999,
};

export const Shadows = {
  sm: {
    shadowColor: Colors.shadow,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 1,
    shadowRadius: 2,
    elevation: 2,
  },
  md: {
    shadowColor: Colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 4,
    elevation: 4,
  },
  lg: {
    shadowColor: Colors.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 8,
  },
  xl: {
    shadowColor: Colors.shadow,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 1,
    shadowRadius: 16,
    elevation: 16,
  },
};

// Custom Icon Names
export const Icons = {
  // Navigation
  home: 'home',
  camera: 'camera',
  profile: 'person',
  analytics: 'analytics',
  
  // Analysis
  sleep: 'moon',
  skin: 'sparkles',
  score: 'star',
  trend: 'trending-up',
  trendDown: 'trending-down',
  trendStable: 'remove',
  
  // Features
  darkCircles: 'eye-off',
  puffiness: 'water',
  brightness: 'sunny',
  wrinkles: 'layers',
  texture: 'grid',
  
  // Actions
  scan: 'scan',
  save: 'bookmark',
  share: 'share',
  refresh: 'refresh',
  settings: 'settings',
  info: 'information-circle',
  
  // Status
  success: 'checkmark-circle',
  warning: 'warning',
  error: 'close-circle',
  
  // Skincare
  cleanser: 'water',
  moisturizer: 'leaf',
  serum: 'flask',
  sunscreen: 'sunny',
  retinol: 'diamond',
  vitaminC: 'flash',
  exfoliant: 'sparkles',
  toner: 'droplet',
  mask: 'layers',
  
  // Lifestyle
  waterIntake: 'water',
  exercise: 'fitness',
  stress: 'heart',
  nutrition: 'nutrition',
  
  // UI Elements
  chevronRight: 'chevron-forward',
  chevronLeft: 'chevron-back',
  chevronUp: 'chevron-up',
  chevronDown: 'chevron-down',
  close: 'close',
  add: 'add',
  remove: 'remove',
  edit: 'create',
  delete: 'trash',
  search: 'search',
  filter: 'filter',
  sort: 'swap-vertical',
  menu: 'menu',
  more: 'ellipsis-horizontal',
  check: 'checkmark',
  
  // Additional icons for components
  sparkles: 'sparkles',
  grid: 'grid',
  zap: 'flash',
  heart: 'heart',
  star: 'star',
  layers: 'layers',
  sun: 'sunny',
  droplet: 'water-outline',
  moon: 'moon',
  calendar: 'calendar',
  lightbulb: 'bulb',
  lock: 'lock-closed',
  fire: 'flame',
  trophy: 'trophy',
  user: 'person',
  'log-in': 'log-in',
  'log-out': 'log-out',
  'user-plus': 'person-add',
  bell: 'notifications',
  database: 'server',
  'help-circle': 'help-circle',
  'alert-triangle': 'alert',
  'trash-2': 'trash',
  award: 'medal',
  target: 'radio-button-on',
  'logo-google': 'logo-google',
  'logo-apple': 'logo-apple',
  'chevron-left': 'chevron-back',
  'alert-circle': 'alert-circle',
  'check-circle': 'checkmark-circle',
  mail: 'mail',
  smartphone: 'phone-portrait',
  eye: 'eye',
  'eye-off': 'eye-off',
  flask: 'flask',
  leaf: 'leaf',
  checkmark: 'checkmark',
  'camera-reverse': 'camera-reverse',
  image: 'image',
};

// Score Colors
export const getScoreColor = (score: number) => {
  if (score >= 80) return Colors.success;
  if (score >= 60) return Colors.warning;
  if (score >= 40) return Colors.error;
  return Colors.textTertiary;
};

// Score Labels
export const getScoreLabel = (score: number) => {
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Fair';
  return 'Needs Improvement';
};

// Feature Labels
export const getFeatureLabel = (feature: string) => {
  const labels: { [key: string]: string } = {
    dark_circles: 'Dark Circles',
    puffiness: 'Puffiness',
    brightness: 'Brightness',
    wrinkles: 'Wrinkles',
    texture: 'Texture',
  };
  return labels[feature] || feature;
};

// Feature Colors
export const getFeatureColor = (value: number) => {
  if (value >= 80) return Colors.success;
  if (value >= 60) return Colors.warning;
  if (value >= 40) return Colors.error;
  return Colors.textTertiary;
};

// Gradient Colors - Apple-style gradients
export const Gradients = {
  primary: ['#007AFF', '#0056CC'],
  secondary: ['#5856D6', '#3A39A3'],
  accent: ['#FF9500', '#CC7700'],
  success: ['#34C759', '#2AA44A'],
  warning: ['#FF9500', '#CC7700'],
  error: ['#FF3B30', '#CC2E26'],
  surface: [Colors.surface, Colors.surfaceSecondary],
  // Apple-style dark gradients
  darkPrimary: ['#1C1C1E', '#2C2C2E'],
  darkSurface: ['#2C2C2E', '#3A3A3C'],
  darkCard: ['#2C2C2E', '#48484A'],
  // Subtle gradients for depth
  subtle: ['rgba(255, 255, 255, 0.05)', 'rgba(255, 255, 255, 0.02)'],
  subtleDark: ['rgba(0, 0, 0, 0.1)', 'rgba(0, 0, 0, 0.05)'],
};

// Theme-aware color functions
export const getThemeColors = (isDark: boolean) => {
  return isDark ? Colors.dark : Colors.light;
};

export const getThemeGradients = (isDark: boolean) => {
  return isDark ? {
    primary: Gradients.darkPrimary,
    secondary: Gradients.darkSurface,
    surface: Gradients.darkCard,
    subtle: Gradients.subtleDark,
  } : {
    primary: Gradients.primary,
    secondary: Gradients.secondary,
    surface: Gradients.surface,
    subtle: Gradients.subtle,
  };
};

// Button Styles
export const ButtonStyles = {
  // Primary Button (filled with primary color)
  primary: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing['2xl'],
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: Spacing.sm,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  
  // Primary Button with flex (for equal sizing)
  primaryFlex: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing['2xl'],
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: Spacing.sm,
    flex: 1,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  
  // Secondary Button (glass morphic blue background)
  secondary: {
    backgroundColor: 'rgba(0, 122, 255, 0.15)',
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing['2xl'],
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: Spacing.sm,
    borderWidth: 1,
    borderColor: 'rgba(0, 122, 255, 0.3)',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
  },
  
  // Secondary Button with flex (for equal sizing)
  secondaryFlex: {
    backgroundColor: 'rgba(0, 122, 255, 0.15)',
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing['2xl'],
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: Spacing.sm,
    flex: 1,
    borderWidth: 1,
    borderColor: 'rgba(0, 122, 255, 0.3)',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
  },
  
  // Success Button
  success: {
    backgroundColor: Colors.success,
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing['2xl'],
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: Spacing.sm,
    shadowColor: Colors.success,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  
  // Success Button with flex
  successFlex: {
    backgroundColor: Colors.success,
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing['2xl'],
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: Spacing.sm,
    flex: 1,
    shadowColor: Colors.success,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  
  // Error Button
  error: {
    backgroundColor: Colors.error,
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing['2xl'],
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: Spacing.sm,
    shadowColor: Colors.error,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  
  // Error Button with flex
  errorFlex: {
    backgroundColor: Colors.error,
    borderRadius: BorderRadius.full,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing['2xl'],
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: Spacing.sm,
    flex: 1,
    shadowColor: Colors.error,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  
  // Button Text Styles
  text: {
    primary: {
      color: Colors.textInverse,
      fontSize: Typography.fontSize.base,
      fontWeight: '600' as any,
      fontFamily: Typography.fontFamily.primary,
    },
    secondary: {
      color: Colors.primary,
      fontSize: Typography.fontSize.base,
      fontWeight: '600' as any,
      fontFamily: Typography.fontFamily.primary,
    },
    success: {
      color: Colors.textInverse,
      fontSize: Typography.fontSize.base,
      fontWeight: '600' as any,
      fontFamily: Typography.fontFamily.primary,
    },
    error: {
      color: Colors.textInverse,
      fontSize: Typography.fontSize.base,
      fontWeight: '600' as any,
      fontFamily: Typography.fontFamily.primary,
    },
  },
};

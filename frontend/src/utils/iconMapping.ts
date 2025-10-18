/**
 * Icon Mapping - Maps backend emojis/labels to icon names
 * Uses the existing CustomIcon component (Ionicons via @expo/vector-icons)
 */

import { Icons } from '../design/DesignSystem';

/**
 * Feature icons - for individual facial features
 */
export const featureIconMap: Record<string, keyof typeof Icons> = {
  dark_circles: 'darkCircles',
  puffiness: 'puffiness',
  brightness: 'brightness',
  wrinkles: 'wrinkles',
  texture: 'texture',
  pore_size: 'texture',
};

/**
 * Status icons - for overall status/fun labels
 */
export const statusIconMap: Record<string, keyof typeof Icons> = {
  excellent: 'score',
  good: 'trend',
  fair: 'trendStable',
  needs_care: 'sleep',
  poor: 'trendDown',
};

/**
 * Insight type icons - for insight messages
 */
export const insightIconMap: Record<string, keyof typeof Icons> = {
  info: 'analytics',
  warning: 'warning',
  success: 'success',
  focus: 'scan',
};

/**
 * Category icons - for recommendations
 */
export const categoryIconMap: Record<string, keyof typeof Icons> = {
  sleep: 'sleep',
  hydration: 'waterIntake',
  skincare: 'skin',
  general: 'analytics',
};

/**
 * Helper function to replace emoji with icon name
 */
export function getIconForEmoji(text: string): keyof typeof Icons | null {
  const emojiMap: Record<string, keyof typeof Icons> = {
    '👁️': 'darkCircles',
    '💧': 'waterIntake',
    '✨': 'skin',
    '📏': 'analytics',
    '🧽': 'texture',
    '🔍': 'scan',
    '📊': 'analytics',
    '⚠️': 'warning',
    '✅': 'success',
    '💤': 'sleep',
  };

  for (const [emoji, iconName] of Object.entries(emojiMap)) {
    if (text.includes(emoji)) {
      return iconName;
    }
  }
  return null;
}

/**
 * Helper to remove emojis from text
 */
export function stripEmojis(text: string): string {
  // Remove common emojis used in the app
  return text.replace(/[📊⚠️✅👁️💧✨📏🧽🔍💤🌟💪🌱🎯👑😐🧟😴]/g, '').trim();
}

import React from 'react';
import { View } from 'react-native';
import CustomIcon from './CustomIcon';
import { Icons } from '../design/DesignSystem';

interface FeatureIconProps {
  feature?: string;
  status?: string;
  type?: 'feature' | 'status' | 'insight';
  size?: number;
  color?: string;
  style?: any;
}

/**
 * FeatureIcon - Renders appropriate icon based on feature/status using CustomIcon
 * 
 * Usage:
 *   <FeatureIcon feature="dark_circles" size={24} />
 *   <FeatureIcon status="excellent" type="status" />
 */
export const FeatureIcon: React.FC<FeatureIconProps> = ({
  feature,
  status,
  type = 'feature',
  size = 20,
  color,
  style
}) => {
  // Map feature/status to icon names from DesignSystem
  const featureIconMap: Record<string, keyof typeof Icons> = {
    dark_circles: 'darkCircles',
    puffiness: 'puffiness',
    brightness: 'brightness',
    wrinkles: 'wrinkles',
    texture: 'texture',
    pore_size: 'texture',
  };

  const statusIconMap: Record<string, keyof typeof Icons> = {
    excellent: 'score',
    good: 'trend',
    fair: 'trendStable',
    needs_care: 'sleep',
    poor: 'trendDown',
  };

  let iconName: keyof typeof Icons | undefined;

  if (type === 'feature' && feature) {
    iconName = featureIconMap[feature];
  } else if (type === 'status' && status) {
    iconName = statusIconMap[status];
  }

  if (!iconName) {
    return <View style={style} />;
  }

  return <CustomIcon name={iconName} size={size} color={color} style={style} />;
};

export default FeatureIcon;

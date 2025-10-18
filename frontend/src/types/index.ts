export interface User {
  id: string;
  email?: string;
  displayName?: string;
  photoURL?: string;
  isGuest: boolean;
  isPremium: boolean;
  streakCount: number;
  createdAt: Date;
  lastActive: Date;
}

export interface RoutineData {
  sleep_hours?: number;
  water_intake?: number;
  product_used?: string; // Keep for backward compatibility
  skincare_products?: string[]; // New array for multiple products
  daily_note?: string;
}

export interface AnalysisResult {
  user_id: string;
  date: string;
  image_uri?: string; // Store the image URI for gallery
  sleep_score: number;
  skin_health_score: number;
  features: {
    dark_circles: number;
    puffiness: number;
    brightness: number;
    wrinkles: number;
    texture: number;
  };
  routine?: RoutineData;
  fun_label: string;
  confidence: number;
  smart_summary?: {
    daily_summary: string;
    key_insights: string[];
    recommendations: string[];
  };
}

export interface DailySummary {
  daily_summary: string;
  sleep_score_change?: number;
  skin_health_change?: number;
  key_insights: string[];
  recommendations: string[];
  natural_remedies?: string[];
  product_recommendations?: string[];
  lifestyle_tip?: string;
}

export interface WeeklySummary {
  weekly_summary: string;
  average_sleep_score: number;
  average_skin_health_score: number;
  score_trend: 'improving' | 'declining' | 'stable';
  lifestyle_insights: string[];
  routine_effectiveness: string[];
}

export interface SkincareProduct {
  id: string;
  name: string;
  category: 'cleanser' | 'moisturizer' | 'serum' | 'sunscreen' | 'treatment' | 'mask' | 'toner' | 'exfoliant';
  benefits: string[];
  usage: 'morning' | 'evening' | 'both';
}

export interface StreakData {
  current_streak: number;
  longest_streak: number;
  last_scan_date?: string;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked_at?: Date;
  is_unlocked: boolean;
}

export interface ShareableCard {
  sleep_score: number;
  skin_health_score: number;
  fun_label: string;
  weekly_change: number;
  streak_count: number;
  date: string;
}

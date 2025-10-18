import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AnalysisResult, DailySummary, WeeklySummary, StreakData } from '../types';
import { analysisService } from '../services/analysisService';
import { storageService } from '../utils/storage';
import { useAuth } from './AuthContext';

interface AnalysisContextType {
  currentAnalysis: AnalysisResult | null;
  analyses: AnalysisResult[];
  analysisHistory: AnalysisResult[];
  dailySummary: DailySummary | null;
  weeklySummary: WeeklySummary | null;
  weeklyAnalysis: any | null;
  streakData: StreakData;
  isLoading: boolean;
  analyzeImage: (imageUri: string, routineData?: any) => Promise<AnalysisResult>;
  getDailySummary: (date: string) => Promise<DailySummary>;
  getWeeklySummary: (weekStart: string) => Promise<WeeklySummary>;
  getWeeklyAnalysis: (days?: number) => Promise<any>;
  getAnalysisHistory: (days?: number) => Promise<AnalysisResult[]>;
  updateStreak: () => void;
  clearAnalysis: () => void;
  resetAllData: () => Promise<void>;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
};

interface AnalysisProviderProps {
  children: ReactNode;
}

export const AnalysisProvider: React.FC<AnalysisProviderProps> = ({ children }) => {
  const { isGuest, user } = useAuth();
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisResult[]>([]);
  const [dailySummary, setDailySummary] = useState<DailySummary | null>(null);
  const [weeklySummary, setWeeklySummary] = useState<WeeklySummary | null>(null);
  const [weeklyAnalysis, setWeeklyAnalysis] = useState<any | null>(null);
  const [streakData, setStreakData] = useState<StreakData>({
    current_streak: 0,
    longest_streak: 0,
  });
  const [isLoading, setIsLoading] = useState(false);

  // Clear analysis data when user changes (logout/login/guest switch)
  useEffect(() => {
    const clearAnalysisData = () => {
      console.log('🔄 User changed, clearing analysis data');
      setCurrentAnalysis(null);
      setAnalyses([]);
      setAnalysisHistory([]);
      setDailySummary(null);
      setWeeklySummary(null);
      setWeeklyAnalysis(null);
      setStreakData({
        current_streak: 0,
        longest_streak: 0,
        last_scan_date: null,
      });
    };

    // Clear data when user becomes null (logout) or when switching to guest
    if (!user || isGuest) {
      clearAnalysisData();
    }
  }, [user, isGuest]);

  // Additional effect to clear data when switching to guest mode
  useEffect(() => {
    if (isGuest) {
      console.log('👤 Switching to guest mode, clearing all analysis data');
      setCurrentAnalysis(null);
      setAnalyses([]);
      setAnalysisHistory([]);
      setDailySummary(null);
      setWeeklySummary(null);
      setWeeklyAnalysis(null);
      setStreakData({
        current_streak: 0,
        longest_streak: 0,
        last_scan_date: null,
      });
    }
  }, [isGuest]);

  const calculateStreakFromHistory = (historyData?: AnalysisResult[]) => {
    const dataToUse = historyData || analysisHistory;
    
    if (dataToUse.length === 0) {
      console.log('No analysis data found, returning zero streak');
      return {
        current_streak: 0,
        longest_streak: 0,
        last_scan_date: null,
      };
    }

    // Sort analyses by date (newest first)
    const sortedAnalyses = [...dataToUse].sort((a, b) => 
      new Date(b.date).getTime() - new Date(a.date).getTime()
    );

    // Get unique dates (in case multiple scans on same day)
    const uniqueDates = [...new Set(sortedAnalyses.map(analysis => analysis.date))];
    
    console.log('Calculating streak from history:');
    console.log('- Total analyses:', dataToUse.length);
    console.log('- Unique dates:', uniqueDates);
    console.log('- Sorted by date (newest first):', uniqueDates);

    let currentStreak = 0;
    let longestStreak = 0;
    let lastScanDate = null;

    if (uniqueDates.length > 0) {
      lastScanDate = uniqueDates[0]; // Most recent date
      
      // Calculate current streak by counting consecutive days from today backwards
      const today = new Date().toISOString().split('T')[0];
      let checkDate = new Date(today);
      
      console.log('Calculating current streak from today:', today);
      
      // Check if we have a photo from today
      if (uniqueDates.includes(today)) {
        currentStreak = 1;
        checkDate.setDate(checkDate.getDate() - 1);
        
        // Continue counting consecutive days backwards
        while (uniqueDates.includes(checkDate.toISOString().split('T')[0])) {
          currentStreak++;
          checkDate.setDate(checkDate.getDate() - 1);
        }
      } else {
        // No photo today, check if we have photos from previous days
        checkDate.setDate(checkDate.getDate() - 1);
        while (uniqueDates.includes(checkDate.toISOString().split('T')[0])) {
          currentStreak++;
          checkDate.setDate(checkDate.getDate() - 1);
        }
      }
      
      // Calculate longest streak by checking consecutive days in the data
      let tempStreak = 1; // Start with 1 for the first day
      longestStreak = 1;
      
      for (let i = 0; i < uniqueDates.length - 1; i++) {
        const currentDate = new Date(uniqueDates[i]);
        const nextDate = new Date(uniqueDates[i + 1]);
        const diffDays = Math.floor((currentDate.getTime() - nextDate.getTime()) / (1000 * 60 * 60 * 24));
        
        console.log(`Checking ${uniqueDates[i]} vs ${uniqueDates[i + 1]}: ${diffDays} days difference`);
        
        if (diffDays === 1) {
          tempStreak++;
        } else {
          longestStreak = Math.max(longestStreak, tempStreak);
          tempStreak = 1; // Reset to 1 for the next sequence
        }
      }
      longestStreak = Math.max(longestStreak, tempStreak);
    }

    const streakData = {
      current_streak: currentStreak,
      longest_streak: longestStreak,
      last_scan_date: lastScanDate,
    };

    console.log('Final calculated streak:', streakData);
    return streakData;
  };

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const loadAnalysisData = async () => {
    try {
      console.log('Loading analysis data from storage...');
      
      // For guest users, always start fresh - no persistent data
      if (isGuest) {
        console.log('Guest user detected - starting with fresh data');
        setCurrentAnalysis(null);
        setAnalyses([]);
        setAnalysisHistory([]);
        setDailySummary(null);
        setWeeklySummary(null);
        setWeeklyAnalysis(null);
        setStreakData({
          current_streak: 0,
          longest_streak: 0,
          last_scan_date: null,
        });
        return;
      }
      
      // For registered users, start with empty state - no mock data
      console.log('Starting with empty state - no mock data');
      setAnalysisHistory([]);
      setAnalyses([]);
      setStreakData({
        current_streak: 0,
        longest_streak: 0,
        last_scan_date: null,
      });

      // Load current analysis
      const currentData = await storageService.getJSON<AnalysisResult>('currentAnalysis');
      if (currentData) {
        console.log('Loaded current analysis:', currentData);
        setCurrentAnalysis(currentData);
      }
    } catch (error) {
      console.error('Error loading analysis data:', error);
    }
  };

  const saveAnalysisData = async () => {
    try {
      // Guest users should never save data to storage
      if (isGuest) {
        console.log('Guest user - skipping data save to storage');
        return;
      }
      
      console.log('Saving analysis data to storage...');
      await storageService.setJSON('analysisHistory', analysisHistory);
      await storageService.setJSON('streakData', streakData);
      if (currentAnalysis) {
        await storageService.setJSON('currentAnalysis', currentAnalysis);
      }
      console.log('Analysis data saved successfully');
    } catch (error) {
      console.error('Error saving analysis data:', error);
    }
  };

  const analyzeImage = async (imageUri: string, routineData?: any): Promise<AnalysisResult> => {
    try {
      setIsLoading(true);
      
      // Get user_id from auth context
      const userId = isGuest ? 'guest' : (user?.id || 'guest');
      console.log('👤 [ANALYSIS CONTEXT] Using user_id:', userId);
      
      // Call the analysis service with user_id
      const result = await analysisService.analyzeImage(imageUri, routineData, userId);
      
      // Add image URI to the result
      const resultWithImage = {
        ...result,
        image_uri: imageUri
      };
      
      // Update state
      setCurrentAnalysis(resultWithImage);
      
      // Add to history - replace any existing analysis for the same date
      const today = resultWithImage.date;
      const existingHistory = analysisHistory.filter(analysis => analysis.date !== today);
      const newHistory = [resultWithImage, ...existingHistory];
      
      console.log(`Adding analysis for ${today}. Previous analyses for this date removed.`);
      console.log(`Total analyses: ${analysisHistory.length} -> ${newHistory.length}`);
      
      setAnalysisHistory(newHistory);
      setAnalyses(newHistory);
      
      // Update streak
      updateStreak();
      
      // Save to storage
      await saveAnalysisData();
      
      // Refresh weekly analysis to get updated data (only for registered users)
      if (!isGuest) {
        try {
          await getWeeklyAnalysis(7);
        } catch (weeklyError) {
          console.warn('Failed to refresh weekly analysis:', weeklyError);
          // Don't throw - this is not critical for the main analysis
        }
      }
      
      return resultWithImage;
    } catch (error) {
      console.error('Analysis error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const getDailySummary = async (date: string): Promise<DailySummary> => {
    try {
      setIsLoading(true);
      const summary = await analysisService.getDailySummary(date, isGuest, user?.id);
      setDailySummary(summary);
      return summary;
    } catch (error) {
      console.error('Error getting daily summary:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const getWeeklySummary = async (weekStart: string): Promise<WeeklySummary> => {
    try {
      setIsLoading(true);
      const summary = await analysisService.getWeeklySummary(weekStart, isGuest);
      setWeeklySummary(summary);
      return summary;
    } catch (error) {
      console.error('Error getting weekly summary:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const getWeeklyAnalysis = async (days: number = 7): Promise<any> => {
    try {
      setIsLoading(true);
      
      // Guest users don't get weekly analysis - they only get instant analysis
      if (isGuest) {
        const guestResponse = {
          weekly_summary: "Register to unlock weekly insights and track your progress over time!",
          weekly_insights: [],
          weekly_recommendations: [],
          trends: null,
          routine_effectiveness: null,
          smart_analysis: null
        };
        setWeeklyAnalysis(guestResponse);
        return guestResponse;
      }
      
      const analysis = await analysisService.getWeeklyAnalysis(days, isGuest, user?.id);
      setWeeklyAnalysis(analysis);
      return analysis;
    } catch (error) {
      console.error('Error getting weekly analysis:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const getAnalysisHistory = async (days: number = 30): Promise<AnalysisResult[]> => {
    try {
      setIsLoading(true);
      const history = await analysisService.getAnalysisHistory(days, isGuest, user?.id);
      setAnalysisHistory(history);
      return history;
    } catch (error) {
      console.error('Error getting analysis history:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updateStreak = () => {
    const newStreakData = calculateStreakFromHistory();
    setStreakData(newStreakData);
  };

  const clearAnalysis = () => {
    setCurrentAnalysis(null);
    setDailySummary(null);
    setWeeklySummary(null);
    setWeeklyAnalysis(null);
  };

  const resetAllData = async () => {
    try {
      console.log('Resetting all data...');
      try {
        await storageService.clear();
        console.log('Storage cleared successfully');
      } catch (clearError) {
        console.warn('Storage clear had issues but continuing:', clearError);
        // Continue with state reset anyway
      }
      setCurrentAnalysis(null);
      setAnalyses([]);
      setAnalysisHistory([]);
      setDailySummary(null);
      setWeeklySummary(null);
      setWeeklyAnalysis(null);
      setStreakData({
        current_streak: 0,
        longest_streak: 0,
        last_scan_date: null,
      });
      console.log('All data reset successfully');
    } catch (error) {
      console.error('Error resetting data:', error);
    }
  };

  const value: AnalysisContextType = {
    currentAnalysis,
    analyses,
    analysisHistory,
    dailySummary,
    weeklySummary,
    weeklyAnalysis,
    streakData,
    isLoading,
    analyzeImage,
    getDailySummary,
    getWeeklySummary,
    getWeeklyAnalysis,
    getAnalysisHistory,
    updateStreak,
    clearAnalysis,
    resetAllData,
  };

  return (
    <AnalysisContext.Provider value={value}>
      {children}
    </AnalysisContext.Provider>
  );
};

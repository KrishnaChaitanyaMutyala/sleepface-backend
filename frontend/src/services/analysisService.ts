import { AnalysisResult, DailySummary, WeeklySummary } from '../types';
import { ImageCompression } from '../utils/imageCompression';

const API_BASE_URL = 'http://192.168.0.165:8000'; // Updated for mobile device access

class AnalysisService {
  private async makeRequest<T>(
    endpoint: string,
    method: 'GET' | 'POST' = 'GET',
    body?: any
  ): Promise<T> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      console.log(`🌐 Making ${method} request to: ${url}`);
      
      const options: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (body) {
        if (body instanceof FormData) {
          // For file uploads, don't set Content-Type header
          console.log('📁 Body is FormData, removing Content-Type header');
          const headers = { ...options.headers };
          delete (headers as any)['Content-Type'];
          options.headers = headers;
          options.body = body;
        } else {
          console.log('📄 Body is JSON, stringifying...');
          options.body = JSON.stringify(body);
        }
      }

      console.log('🚀 Sending request with options:', {
        method: options.method,
        headers: options.headers,
        hasBody: !!options.body
      });

      const response = await fetch(url, options);
      
      console.log(`📡 Response received: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.log('❌ Error response body:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ Response parsed successfully:', result);
      return result;
    } catch (error) {
      console.error(`💥 API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async analyzeImage(imageUri: string, routineData?: any, userId?: string): Promise<AnalysisResult> {
    try {
      console.log('🔄 Starting image analysis...');
      console.log('📸 Image URI:', imageUri);
      console.log('📋 Routine data:', routineData);
      console.log('👤 User ID:', userId || 'guest');

      // Compress image for faster upload
      console.log('🖼️ Compressing image for faster upload...');
      const networkQuality = await ImageCompression.detectNetworkQuality();
      const compressionOptions = ImageCompression.getOptimalSettings(networkQuality);
      const compressedImageUri = await ImageCompression.compressImage(imageUri, compressionOptions);
      
      console.log('✅ Image compressed', { 
        networkQuality, 
        compressionOptions,
        compressedUri: compressedImageUri 
      });

      // Create FormData for file upload
      const formData = new FormData();
      
      // For React Native, we need to create the file object properly
      const file = {
        uri: compressedImageUri, // Use compressed image
        type: 'image/jpeg',
        name: 'selfie.jpg',
      };
      
      formData.append('file', file as any);
      formData.append('user_id', userId || 'guest');  // ✅ FIX: Send user_id to backend!
      
      if (routineData) {
        formData.append('routine_data', JSON.stringify(routineData));
      }

      console.log('📤 Sending image to backend for analysis...');
      console.log('🌐 Backend URL:', `${API_BASE_URL}/analyze`);
      
      try {
        // Try to connect to real backend first
        const result = await this.makeRequest<AnalysisResult>('/analyze', 'POST', formData);
        console.log('✅ Backend analysis successful!');
        console.log('📊 Backend analysis result:', result);
        return result;
      } catch (backendError) {
        console.log('❌ Backend not available, using enhanced mock data');
        console.log('🔍 Backend error details:', backendError);
        // If backend fails, return enhanced mock data based on image
        return this.getEnhancedMockAnalysisResult(imageUri, routineData);
      }
    } catch (error) {
      console.error('💥 Error analyzing image:', error);
      // Return enhanced mock data on error
      return this.getEnhancedMockAnalysisResult(imageUri, routineData);
    }
  }

  async getDailySummary(date: string, isGuest: boolean = false, userId?: string): Promise<DailySummary> {
    // Guest users don't have persistent data, so return fallback immediately
    if (isGuest) {
      console.log('👤 Guest user - returning fallback daily summary');
      return {
        daily_summary: "Take your first selfie to get your daily summary!",
        key_insights: ["Take your first selfie to get personalized insights!"],
        recommendations: ["Take your first selfie to get personalized recommendations!"]
      };
    }

    try {
      if (!userId) {
        throw new Error('User ID not available');
      }
      
      console.log('📊 Requesting daily summary from backend...');
      console.log('📅 Date:', date);
      console.log('👤 User ID:', userId);
      
      // Try to get real summary from backend for registered users
      const summary = await this.makeRequest<DailySummary>(`/user/${userId}/summary?date=${date}`);
      console.log('✅ Daily summary received from backend:', summary);
      return summary;
    } catch (error) {
      console.log('❌ Backend daily summary not available, using fallback');
      console.log('🔍 Error details:', error);
      
      // Fallback to basic message
      return {
        daily_summary: "Take your first selfie to get your daily summary!",
        key_insights: ["Take your first selfie to get personalized insights!"],
        recommendations: ["Take your first selfie to get personalized recommendations!"]
      };
    }
  }

  async getWeeklySummary(weekStart: string, isGuest: boolean = false): Promise<WeeklySummary> {
    // Guest users don't have persistent data, so return fallback immediately
    if (isGuest) {
      console.log('👤 Guest user - returning fallback weekly summary');
      return {
        weekly_summary: "Take some selfies this week to get your weekly summary!",
        average_sleep_score: 0,
        average_skin_health_score: 0,
        score_trend: 'stable' as const,
        lifestyle_insights: ["Take some selfies to get lifestyle insights!"],
        routine_effectiveness: ["Take some selfies to see routine effectiveness!"]
      };
    }

    try {
      // Try to get real summary from backend for registered users
      return await this.makeRequest<WeeklySummary>(`/user/weekly-summary?week_start=${weekStart}`);
    } catch (error) {
      console.error('Error getting weekly summary:', error);
      return {
        weekly_summary: "Take some selfies this week to get your weekly summary!",
        average_sleep_score: 0,
        average_skin_health_score: 0,
        score_trend: 'stable' as const,
        lifestyle_insights: ["Take some selfies to get lifestyle insights!"],
        routine_effectiveness: ["Take some selfies to see routine effectiveness!"]
      };
    }
  }

  async getWeeklyAnalysis(days: number = 7, isGuest: boolean = false, userId?: string): Promise<any> {
    // Guest users don't have persistent data, so return fallback immediately
    if (isGuest) {
      console.log('👤 Guest user - returning fallback weekly analysis');
      return {
        weekly_summary: "Take more selfies this week to get your weekly analysis!",
        weekly_insights: ["Take more selfies this week to get personalized insights!"],
        weekly_recommendations: ["Take more selfies this week to get personalized recommendations!"],
        trends: { insufficient_data: true },
        routine_effectiveness: { insufficient_data: true },
        smart_analysis: { insufficient_data: true },
        analysis_period: "Insufficient data",
        data_points: 0
      };
    }

    try {
      if (!userId) {
        throw new Error('User ID not available');
      }
      
      console.log('📊 Requesting weekly analysis from backend...');
      console.log('📅 Days:', days);
      console.log('👤 User ID:', userId);
      
      // Try to get real weekly analysis from backend for registered users
      const analysis = await this.makeRequest<any>(`/user/${userId}/weekly-analysis?days=${days}`);
      console.log('✅ Weekly analysis received from backend:', analysis);
      return analysis;
    } catch (error) {
      console.log('❌ Backend weekly analysis not available, using fallback');
      console.log('🔍 Error details:', error);
      
      // Fallback to basic message
      return {
        weekly_summary: "Take more selfies this week to get your weekly analysis!",
        weekly_insights: ["Take more selfies this week to get personalized insights!"],
        weekly_recommendations: ["Take more selfies this week to get personalized recommendations!"],
        trends: { insufficient_data: true },
        routine_effectiveness: { insufficient_data: true },
        smart_analysis: { insufficient_data: true },
        analysis_period: "Insufficient data",
        data_points: 0
      };
    }
  }

  async getAnalysisHistory(days: number = 30, isGuest: boolean = false, userId?: string): Promise<AnalysisResult[]> {
    // Guest users don't have persistent data, so return empty array immediately
    if (isGuest) {
      console.log('👤 Guest user - returning empty analysis history');
      return [];
    }

    try {
      if (!userId) {
        throw new Error('User ID not available');
      }
      
      console.log('📊 Requesting analysis history from backend...');
      console.log('📅 Days:', days);
      console.log('👤 User ID:', userId);
      
      // Try to get real history from backend for registered users
      const response = await this.makeRequest<{history: AnalysisResult[]}>(`/user/${userId}/history?days=${days}`);
      return response.history;
    } catch (error) {
      console.error('Error getting analysis history:', error);
      return [];
    }
  }

  // Enhanced mock data methods for development
  private getEnhancedMockAnalysisResult(imageUri: string, routineData?: any): AnalysisResult {
    // Generate more realistic scores based on time of day and routine data
    const now = new Date();
    const hour = now.getHours();
    
    // Base scores influenced by time of day
    let baseSleepScore = 50;
    let baseSkinScore = 50;
    
    if (hour >= 6 && hour <= 10) {
      // Morning - typically better scores
      baseSleepScore = 65;
      baseSkinScore = 70;
    } else if (hour >= 11 && hour <= 16) {
      // Afternoon - moderate scores
      baseSleepScore = 55;
      baseSkinScore = 60;
    } else if (hour >= 17 && hour <= 22) {
      // Evening - lower scores due to tiredness
      baseSleepScore = 45;
      baseSkinScore = 55;
    } else {
      // Night - lowest scores
      baseSleepScore = 35;
      baseSkinScore = 45;
    }
    
    // Adjust based on routine data
    if (routineData?.sleep_hours) {
      if (routineData.sleep_hours >= 8) {
        baseSleepScore += 15;
        baseSkinScore += 10;
      } else if (routineData.sleep_hours >= 7) {
        baseSleepScore += 10;
        baseSkinScore += 5;
      } else if (routineData.sleep_hours < 6) {
        baseSleepScore -= 15;
        baseSkinScore -= 10;
      }
    }
    
    if (routineData?.water_intake) {
      if (routineData.water_intake >= 8) {
        baseSkinScore += 15;
      } else if (routineData.water_intake >= 6) {
        baseSkinScore += 10;
      } else if (routineData.water_intake < 4) {
        baseSkinScore -= 15;
      }
    }
    
    // Adjust based on skin care products
    if (routineData?.product_used) {
      const products = routineData.product_used.toLowerCase();
      if (products.includes('vitamin c') || products.includes('vitamin c serum')) {
        baseSkinScore += 8;
      }
      if (products.includes('retinol') || products.includes('retinoid')) {
        baseSkinScore += 10;
      }
      if (products.includes('moisturizer') || products.includes('hydrating')) {
        baseSkinScore += 5;
      }
      if (products.includes('sunscreen') || products.includes('spf')) {
        baseSkinScore += 6;
      }
      if (products.includes('exfoliant') || products.includes('aha') || products.includes('bha')) {
        baseSkinScore += 7;
      }
    }
    
    // Add some randomness but keep it realistic
    const sleepScore = Math.round(Math.max(10, Math.min(95, baseSleepScore + (Math.random() * 20 - 10))));
    const skinScore = Math.round(Math.max(10, Math.min(95, baseSkinScore + (Math.random() * 20 - 10))));
    
    // Generate features based on scores - round to integers
    const features = {
      dark_circles: Math.round(sleepScore < 50 ? -(Math.random() * 30 + 10) : Math.random() * 20 - 10),
      puffiness: Math.round(sleepScore < 40 ? -(Math.random() * 25 + 5) : Math.random() * 15 - 5),
      brightness: Math.round(skinScore > 60 ? Math.random() * 30 + 10 : Math.random() * 20 - 10),
      wrinkles: Math.round(skinScore < 50 ? -(Math.random() * 20 + 5) : Math.random() * 10 - 5),
      texture: Math.round(skinScore > 70 ? Math.random() * 25 + 5 : Math.random() * 15 - 5),
      pore_size: Math.round(skinScore < 60 ? -(Math.random() * 25 + 5) : Math.random() * 15 - 5),
    };
    
    // Generate fun label based on scores and routine
    let funLabel = 'Normal Day 😐';
    
    // Check for specific routine-based labels first
    if (routineData?.product_used) {
      const products = routineData.product_used.toLowerCase();
      if (products.includes('vitamin c') && skinScore >= 70) {
        funLabel = 'Vitamin C Glow ✨';
      } else if (products.includes('retinol') && skinScore >= 75) {
        funLabel = 'Retinol Queen 👑';
      } else if (products.includes('sunscreen') && skinScore >= 65) {
        funLabel = 'Sun Safe & Glowing ☀️';
      }
    }
    
    if (routineData?.water_intake >= 8 && skinScore >= 70) {
      funLabel = 'Hydration Hero 💧';
    }
    
    if (routineData?.sleep_hours >= 8 && sleepScore >= 75) {
      funLabel = 'Beauty Sleep Champion 😴';
    }
    
    // Fallback to score-based labels
    if (funLabel === 'Normal Day 😐') {
      if (sleepScore >= 80 && skinScore >= 80) {
        funLabel = 'Glow Queen 👑';
      } else if (sleepScore >= 70 && skinScore >= 70) {
        funLabel = 'Glow Up 🌟';
      } else if (sleepScore < 40 || skinScore < 40) {
        funLabel = 'Zombie Mode 🧟';
      } else if (sleepScore < 50) {
        funLabel = 'Sleepy Head 😴';
      } else if (skinScore < 50) {
        funLabel = 'Needs TLC 💆‍♀️';
      }
    }
    
    // Generate smart summary based on analysis
    const smartSummary = this.generateSmartSummary(sleepScore, skinScore, features, routineData);
    
    return {
      user_id: 'guest_user',
      date: new Date().toISOString().split('T')[0],
      sleep_score: sleepScore,
      skin_health_score: skinScore,
      features,
      routine: routineData || {
        sleep_hours: null,
        water_intake: null,
        product_used: null,
        daily_note: null,
      },
      fun_label: funLabel,
      confidence: Math.round((0.85 + Math.random() * 0.1) * 100) / 100, // 0.85-0.95 rounded to 2 decimals
      smart_summary: smartSummary,
    };
  }

  private generateSmartSummary(sleepScore: number, skinScore: number, features: any, routineData?: any) {
    const overallHealth = (sleepScore + skinScore) / 2;
    
    // Generate daily summary
    let dailySummary = "";
    if (overallHealth < 30) {
      dailySummary = `Analysis Complete: Your Sleep Score (${sleepScore}/100) and Skin Health Score (${skinScore}/100) show great potential for improvement. We've identified some key areas where small lifestyle changes can make a big difference in how you look and feel.`;
    } else if (overallHealth < 50) {
      dailySummary = `Health Assessment: Your Sleep Score (${sleepScore}/100) and Skin Health Score (${skinScore}/100) show a good foundation with room to grow. Our analysis found specific opportunities to enhance your wellness and skin health.`;
    } else if (overallHealth < 80) {
      dailySummary = `Great Health Metrics: Your Sleep Score (${sleepScore}/100) and Skin Health Score (${skinScore}/100) show you're doing well! Our analysis confirms you're on the right track with potential for even better results.`;
    } else {
      dailySummary = `Outstanding Results: Your Sleep Score (${sleepScore}/100) and Skin Health Score (${skinScore}/100) are excellent! Our analysis shows you're maintaining fantastic health habits that are clearly working for you.`;
    }
    
    // Generate insights based on features
    const insights = [];
    
    if (features.dark_circles < -50) {
      insights.push("Under-Eye Area Focus: Your under-eye area shows room for improvement. Better sleep quality, increased hydration, and gentle eye care can help brighten this area.");
    } else if (features.dark_circles > 20) {
      insights.push("Excellent Under-Eye Area: Your orbital region looks bright and healthy. Your sleep patterns and circulation are working well for this area.");
    }
    
    if (features.puffiness < -50) {
      insights.push("Eye Area Refresh: Your eye area shows some puffiness that can be reduced with better sleep position, reduced sodium intake, and gentle lymphatic massage.");
    } else if (features.puffiness > 20) {
      insights.push("Perfect Eye Contour: Your eye area looks well-defined and refreshed. Your sleep and hydration habits are working great for this area.");
    }
    
    if (features.brightness < -50) {
      insights.push("Skin Glow Enhancement: Your skin could benefit from more radiance. Regular exfoliation, increased hydration, and vitamin C can help bring back that healthy glow.");
    } else if (features.brightness > 20) {
      insights.push("Beautiful Skin Radiance: Your complexion has a lovely natural glow. Your skincare routine and lifestyle habits are working perfectly for healthy, radiant skin.");
    }
    
    if (features.wrinkles < -50) {
      insights.push("Skin Smoothness Focus: Your skin could benefit from more smoothing treatments. Retinol, hyaluronic acid, and consistent sun protection can help improve skin texture.");
    } else if (features.wrinkles > 20) {
      insights.push("Excellent Skin Smoothness: Your skin looks smooth and youthful. Your anti-aging routine and sun protection habits are working beautifully.");
    }
    
    if (features.texture < -50) {
      insights.push("Skin Texture Improvement: Your skin could benefit from smoother texture. Gentle exfoliation, consistent moisturizing, and proper hydration can help create a more even surface.");
    } else if (features.texture > 20) {
      insights.push("Beautiful Skin Texture: Your skin feels smooth and even. Your skincare routine and hydration habits are creating perfect skin texture.");
    }
    
    if (features.pore_size < -50) {
      insights.push("Pore Refinement Focus: Your pores could benefit from tightening treatments. Niacinamide, retinol, and gentle exfoliation can help minimize pore appearance.");
    } else if (features.pore_size > 20) {
      insights.push("Excellent Pore Condition: Your pores look refined and well-maintained. Your skincare routine is working beautifully for pore health.");
    }
    
    // Generate recommendations
    const recommendations = [];
    
    if (sleepScore < 30) {
      recommendations.push("Sleep Optimization Protocol: Implement a 7-9 hour sleep schedule with consistent bedtime. Create a pre-sleep routine including 1-hour screen-free period, cool room temperature (65-68°F), and relaxation techniques.");
    } else if (sleepScore > 80) {
      recommendations.push("Maintain Excellent Sleep Habits: Your sleep patterns are optimal. Continue your current routine and consider advanced sleep tracking to monitor REM cycles and deep sleep quality.");
    }
    
    if (skinScore < 30) {
      recommendations.push("Hydration Protocol: Increase water intake to 2.5-3 liters daily. Add electrolytes and consider hyaluronic acid supplements. Use a humidifier in your bedroom to maintain 40-60% humidity.");
    } else if (skinScore > 80) {
      recommendations.push("Advanced Skincare Maintenance: Your skin health is excellent. Consider professional treatments like microdermabrasion or chemical peels for further enhancement. Maintain your current routine and add antioxidant serums for long-term protection.");
    }
    
    if (features.dark_circles < -20) {
      recommendations.push("Under-Eye Treatment: Use caffeine-based eye creams, cold compresses for 10 minutes daily, and consider professional treatments like PRP or dermal fillers for severe cases.");
    }
    
    if (features.puffiness < -20) {
      recommendations.push("Puffiness Reduction: Reduce sodium intake to <2g daily, elevate head while sleeping, use cold therapy, and consider lymphatic drainage massage.");
    }
    
    if (features.brightness < -20) {
      recommendations.push("Radiance Enhancement: Use vitamin C serum (15-20% L-ascorbic acid), gentle exfoliation with glycolic acid, and brightening ingredients like niacinamide, arbutin, or licorice root extract.");
    }
    
    if (features.wrinkles < -20) {
      recommendations.push("Anti-Aging Protocol: Start with retinol 0.25% twice weekly, increase to daily over 8 weeks. Use peptides, growth factors, and always apply SPF 50+ sunscreen.");
    }
    
    if (features.texture < -20) {
      recommendations.push("Texture Improvement: Use gentle chemical exfoliants (AHA/BHA) 2-3 times weekly, maintain consistent moisturization, and consider professional treatments like microdermabrasion or chemical peels.");
    }
    
    if (features.pore_size < -20) {
      recommendations.push("Pore Minimizing Protocol: Use niacinamide 4-5% twice daily, gentle BHA exfoliant 2-3 times weekly, and always apply non-comedogenic sunscreen. Consider professional treatments like microneedling for severe cases.");
    }
    
    return {
      daily_summary: dailySummary,
      key_insights: insights,
      recommendations: recommendations
    };
  }

  private getMockAnalysisResult(): AnalysisResult {
    const scores = {
      sleep_score: Math.floor(Math.random() * 40) + 30, // 30-70
      skin_health_score: Math.floor(Math.random() * 40) + 30, // 30-70
    };

    const features = {
      dark_circles: Math.floor(Math.random() * 60) - 30, // -30 to 30
      puffiness: Math.floor(Math.random() * 60) - 30,
      brightness: Math.floor(Math.random() * 60) - 30,
      wrinkles: Math.floor(Math.random() * 60) - 30,
      texture: Math.floor(Math.random() * 60) - 30,
      pore_size: Math.floor(Math.random() * 60) - 30,
    };

    const funLabels = [
      'Glow Queen 👑',
      'Glow Up 🌟',
      'Normal Day 😐',
      'Zombie Mode 🧟',
      'Sleepy Head 😴',
    ];

    return {
      user_id: 'guest_user',
      date: new Date().toISOString().split('T')[0],
      sleep_score: scores.sleep_score,
      skin_health_score: scores.skin_health_score,
      features,
      routine: {
        sleep_hours: Math.floor(Math.random() * 4) + 6, // 6-10 hours
        water_intake: Math.floor(Math.random() * 6) + 2, // 2-8 glasses
        product_used: 'Glow Cream',
        daily_note: 'Feeling good today!',
      },
      fun_label: funLabels[Math.floor(Math.random() * funLabels.length)],
      confidence: 0.85,
    };
  }

  private getMockDailySummary(): DailySummary {
    // This would be called with actual analysis data in a real implementation
    return {
      daily_summary: "Take your first selfie to get your personalized daily summary!",
      sleep_score_change: 0,
      skin_health_change: 0,
      key_insights: [
        "Start tracking your sleep and skin health daily",
        "Take a selfie to get AI-powered insights",
        "Build healthy habits with personalized recommendations"
      ],
      recommendations: [
        "Take your first selfie to begin tracking",
        "Set a consistent bedtime routine",
        "Stay hydrated throughout the day"
      ],
    };
  }

  private getMockWeeklySummary(): WeeklySummary {
    return {
      weekly_summary: "This week your average Sleep Score was 68 (+7 vs last week). Your scores are improving this week!",
      average_sleep_score: 68,
      average_skin_health_score: 72,
      score_trend: 'improving',
      lifestyle_insights: [
        "Great sleep habits this week!",
        "Your skin care routine is working well",
        "Consistent water intake helped your glow"
      ],
      routine_effectiveness: [
        "Glow Cream improved brightness by +9% over 7 days",
        "7+ hours of sleep improved your score by 20%"
      ],
    };
  }

  private getMockAnalysisHistory(): AnalysisResult[] {
    const history: AnalysisResult[] = [];
    const today = new Date();
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      const result = this.getMockAnalysisResult();
      result.date = date.toISOString().split('T')[0];
      result.sleep_score = Math.floor(Math.random() * 40) + 30;
      result.skin_health_score = Math.floor(Math.random() * 40) + 30;
      
      history.push(result);
    }
    
    return history.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }
}

export const analysisService = new AnalysisService();

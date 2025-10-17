"""
Data-Driven Smart Summary Service
Generates intelligent summaries based on trend analysis and historical data
No dependency on external LLM APIs - purely data-driven
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics


@dataclass
class FeatureTrend:
    """Represents the trend for a specific facial feature"""
    feature_name: str
    current_value: float
    previous_value: float
    change: float
    change_percentage: float
    trend: str  # 'improving', 'declining', 'stable', 'stagnant'
    duration_days: int
    significance: str  # 'significant', 'moderate', 'minor', 'none'


@dataclass
class TrendInsight:
    """Insights generated from trend analysis"""
    feature: str
    insight: str
    priority: int  # 1 (highest) to 5 (lowest)
    category: str  # 'positive', 'concern', 'neutral'


class SmartSummaryService:
    """
    Data-driven smart summary generation based on historical trends
    Implements the 5-step methodology:
    1. Data Collection (already handled by HistoricalDataService)
    2. Trend Analysis
    3. Change Detection and Thresholds
    4. Duration Monitoring
    5. Summary Generation
    """
    
    def __init__(self):
        # Step 3: Define thresholds for change detection
        self.IMPROVEMENT_THRESHOLD = 2.0  # Points increase considered improvement
        self.DECLINE_THRESHOLD = -2.0     # Points decrease considered decline
        self.STAGNATION_THRESHOLD = 0.5   # Less than this = stagnant
        
        # Step 4: Duration thresholds
        self.STAGNATION_DURATION = 14     # Days without improvement = stagnant
        self.TREND_CONFIRMATION_PERIOD = 7  # Days to confirm a trend
        
        # Feature score ranges (0-100 scale from ai_engine.py)
        self.FEATURE_RANGES = {
            'dark_circles': {'excellent': 75, 'good': 60, 'fair': 45, 'poor': 30},
            'puffiness': {'excellent': 70, 'good': 55, 'fair': 40, 'poor': 25},
            'brightness': {'excellent': 80, 'good': 65, 'fair': 50, 'poor': 35},
            'wrinkles': {'excellent': 75, 'good': 60, 'fair': 45, 'poor': 30},
            'texture': {'excellent': 75, 'good': 60, 'fair': 45, 'poor': 30},
            'pore_size': {'excellent': 70, 'good': 55, 'fair': 40, 'poor': 25}
        }
        
        # Feature display names
        self.FEATURE_NAMES = {
            'dark_circles': 'Dark Circles',
            'puffiness': 'Eye Puffiness',
            'brightness': 'Skin Brightness',
            'wrinkles': 'Fine Lines',
            'texture': 'Skin Texture',
            'pore_size': 'Pore Size'
        }
    
    async def generate_smart_summary(
        self, 
        current_analysis: Dict[str, Any],
        routine: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive smart summary based on data trends
        
        Args:
            current_analysis: Today's analysis result
            routine: Today's routine data
            historical_data: Historical analysis data (sorted by date)
        
        Returns:
            Smart summary with insights and recommendations
        """
        print(f"🧠 [SMART SUMMARY] Generating data-driven summary...")
        print(f"📊 [SMART SUMMARY] Historical data points: {len(historical_data)}")
        
        # Step 1: Handle insufficient data
        if len(historical_data) < 2:
            return self._generate_first_time_summary(current_analysis, routine)
        
        # Step 2: Perform trend analysis
        feature_trends = self._analyze_feature_trends(current_analysis, historical_data)
        
        # Step 3 & 4: Detect changes and monitor duration
        significant_changes = self._detect_significant_changes(feature_trends)
        stagnant_features = self._detect_stagnation(historical_data, current_analysis)
        
        # Step 5: Generate summary based on trends
        daily_summary = self._generate_daily_summary(
            current_analysis, feature_trends, significant_changes, stagnant_features, routine
        )
        
        key_insights = self._generate_key_insights(
            feature_trends, significant_changes, stagnant_features
        )
        
        recommendations = self._generate_recommendations(
            current_analysis, feature_trends, stagnant_features, routine
        )
        
        return {
            "daily_summary": daily_summary,
            "key_insights": key_insights,
            "recommendations": recommendations,
            "trend_analysis": {
                "improving_features": [t.feature_name for t in feature_trends if t.trend == 'improving'],
                "declining_features": [t.feature_name for t in feature_trends if t.trend == 'declining'],
                "stagnant_features": stagnant_features,
                "stable_features": [t.feature_name for t in feature_trends if t.trend == 'stable']
            },
            "model": "Data-Driven Analysis",
            "provider": "internal",
            "data_points_analyzed": len(historical_data)
        }
    
    def _analyze_feature_trends(
        self, 
        current_analysis: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> List[FeatureTrend]:
        """Step 2: Analyze trends for each feature using statistical methods"""
        trends = []
        current_features = current_analysis.get('features', {})
        
        # Get comparison period (last 7 days average vs previous 7 days)
        if len(historical_data) >= 7:
            recent_period = historical_data[-7:]
            comparison_period = historical_data[-14:-7] if len(historical_data) >= 14 else historical_data[:7]
        else:
            recent_period = historical_data
            comparison_period = historical_data[:len(historical_data)//2] if len(historical_data) > 1 else historical_data[:1]
        
        for feature_key, current_value in current_features.items():
            # Calculate average values for comparison
            recent_avg = statistics.mean([
                entry.get('features', {}).get(feature_key, 0) 
                for entry in recent_period
            ])
            
            if comparison_period:
                previous_avg = statistics.mean([
                    entry.get('features', {}).get(feature_key, 0) 
                    for entry in comparison_period
                ])
            else:
                previous_avg = current_value
            
            # Calculate change
            change = recent_avg - previous_avg
            change_percentage = (change / abs(previous_avg)) * 100 if previous_avg != 0 else 0
            
            # Determine trend
            if change >= self.IMPROVEMENT_THRESHOLD:
                trend = 'improving'
                significance = 'significant' if abs(change) >= 5 else 'moderate'
            elif change <= self.DECLINE_THRESHOLD:
                trend = 'declining'
                significance = 'significant' if abs(change) >= 5 else 'moderate'
            elif abs(change) <= self.STAGNATION_THRESHOLD:
                trend = 'stagnant'
                significance = 'none'
            else:
                trend = 'stable'
                significance = 'minor'
            
            trends.append(FeatureTrend(
                feature_name=feature_key,
                current_value=current_value,
                previous_value=previous_avg,
                change=change,
                change_percentage=change_percentage,
                trend=trend,
                duration_days=len(recent_period),
                significance=significance
            ))
        
        return trends
    
    def _detect_significant_changes(self, feature_trends: List[FeatureTrend]) -> List[FeatureTrend]:
        """Step 3: Detect significant changes based on thresholds"""
        return [
            trend for trend in feature_trends 
            if trend.significance in ['significant', 'moderate']
        ]
    
    def _detect_stagnation(
        self, 
        historical_data: List[Dict[str, Any]],
        current_analysis: Dict[str, Any]
    ) -> List[str]:
        """Step 4: Monitor duration and detect stagnant features"""
        stagnant_features = []
        
        if len(historical_data) < self.STAGNATION_DURATION:
            return stagnant_features
        
        # Check last 14 days for stagnation
        recent_period = historical_data[-self.STAGNATION_DURATION:]
        current_features = current_analysis.get('features', {})
        
        for feature_key in current_features.keys():
            # Get all values for this feature in the period
            values = [entry.get('features', {}).get(feature_key, 0) for entry in recent_period]
            
            if not values:
                continue
            
            # Calculate variance and change
            variance = statistics.variance(values) if len(values) > 1 else 0
            total_change = abs(values[-1] - values[0])
            
            # Feature is stagnant if:
            # 1. Low variance (not changing much)
            # 2. Total change is minimal
            # 3. Score is still in "poor" or "fair" range
            if variance < 2.0 and total_change < 2.0:
                feature_range = self.FEATURE_RANGES.get(feature_key, {})
                if current_features[feature_key] < feature_range.get('good', 60):
                    stagnant_features.append(feature_key)
        
        return stagnant_features
    
    def _generate_daily_summary(
        self,
        current_analysis: Dict[str, Any],
        feature_trends: List[FeatureTrend],
        significant_changes: List[FeatureTrend],
        stagnant_features: List[str],
        routine: Dict[str, Any]
    ) -> str:
        """Step 5: Generate overall status message based on trends"""
        sleep_score = current_analysis.get('sleep_score', 0)
        skin_score = current_analysis.get('skin_health_score', 0)
        
        # Count trend types
        improving = len([t for t in feature_trends if t.trend == 'improving'])
        declining = len([t for t in feature_trends if t.trend == 'declining'])
        
        # Generate status based on overall patterns
        if improving >= 3 and declining == 0:
            status = "Excellent progress! "
            message = f"Your Sleep Score is {sleep_score} and Skin Health is {skin_score}. Multiple features are improving—your routine is working beautifully! Keep going! 🌟"
        
        elif improving >= 2 and declining <= 1:
            status = "Good progress! "
            message = f"Sleep Score: {sleep_score}, Skin Health: {skin_score}. You're seeing positive changes in {improving} areas. Stay consistent with your routine! 💪"
        
        elif len(stagnant_features) >= 3:
            status = "Time for changes. "
            message = f"Sleep Score: {sleep_score}, Skin Health: {skin_score}. Some features have plateaued for 2+ weeks. Consider adjusting your routine for better results. 🔄"
        
        elif declining >= 2:
            status = "Needs attention. "
            message = f"Sleep Score: {sleep_score}, Skin Health: {skin_score}. {declining} features are declining. Review your sleep and skincare routine—something may need adjustment. ⚠️"
        
        else:
            status = "Steady progress. "
            message = f"Sleep Score: {sleep_score}, Skin Health: {skin_score}. Your routine is maintaining stability. Stay consistent for continued results! ✨"
        
        return status + message
    
    def _generate_key_insights(
        self,
        feature_trends: List[FeatureTrend],
        significant_changes: List[FeatureTrend],
        stagnant_features: List[str]
    ) -> List[str]:
        """Generate prioritized key insights"""
        insights = []
        
        # Significant improvements (Priority 1)
        for trend in significant_changes:
            if trend.trend == 'improving':
                feature_name = self.FEATURE_NAMES.get(trend.feature_name, trend.feature_name)
                insights.append(
                    f"🎉 {feature_name} improved by {abs(trend.change):.1f} points ({abs(trend.change_percentage):.0f}%) - your efforts are paying off!"
                )
        
        # Significant declines (Priority 2)
        for trend in significant_changes:
            if trend.trend == 'declining':
                feature_name = self.FEATURE_NAMES.get(trend.feature_name, trend.feature_name)
                insights.append(
                    f"⚠️ {feature_name} declined by {abs(trend.change):.1f} points - may need immediate attention"
                )
        
        # Stagnation alerts (Priority 3)
        for feature_key in stagnant_features:
            feature_name = self.FEATURE_NAMES.get(feature_key, feature_key)
            insights.append(
                f"🔄 {feature_name} hasn't improved in 2+ weeks - consider trying different products or methods"
            )
        
        # Excellent features (Priority 4)
        for trend in feature_trends:
            feature_range = self.FEATURE_RANGES.get(trend.feature_name, {})
            if trend.current_value >= feature_range.get('excellent', 75):
                feature_name = self.FEATURE_NAMES.get(trend.feature_name, trend.feature_name)
                if len(insights) < 5:  # Limit total insights
                    insights.append(
                        f"✨ {feature_name} is excellent ({trend.current_value:.0f}/100) - maintain your current routine!"
                    )
        
        return insights[:6]  # Return top 6 insights
    
    def _generate_recommendations(
        self,
        current_analysis: Dict[str, Any],
        feature_trends: List[FeatureTrend],
        stagnant_features: List[str],
        routine: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on trends"""
        recommendations = []
        current_features = current_analysis.get('features', {})
        
        # Recommendations for declining features
        declining = [t for t in feature_trends if t.trend == 'declining']
        for trend in declining[:2]:  # Top 2 declining features
            recs = self._get_feature_recommendations(trend.feature_name, 'declining', current_features.get(trend.feature_name, 0), routine)
            recommendations.extend(recs)
        
        # Recommendations for stagnant features
        for feature_key in stagnant_features[:2]:  # Top 2 stagnant features
            recs = self._get_feature_recommendations(feature_key, 'stagnant', current_features.get(feature_key, 0), routine)
            recommendations.extend(recs)
        
        # General lifestyle recommendations
        sleep_hours = routine.get('sleep_hours', 0)
        water_intake = routine.get('water_intake', 0)
        
        if sleep_hours < 7:
            recommendations.append(f"🛏️ Aim for 7-8 hours of sleep tonight (currently {sleep_hours}h) - critical for skin recovery")
        
        if water_intake < 6:
            recommendations.append(f"💧 Increase water intake to 8+ glasses (currently {water_intake}) for better hydration")
        
        # Product recommendations for improving features
        improving = [t for t in feature_trends if t.trend == 'improving']
        if improving:
            best_feature = max(improving, key=lambda t: abs(t.change))
            recommendations.append(
                f"✅ Continue your current routine - it's working well for {self.FEATURE_NAMES.get(best_feature.feature_name)}!"
            )
        
        return recommendations[:8]  # Top 8 recommendations
    
    def _get_feature_recommendations(
        self, 
        feature_key: str, 
        status: str,
        current_value: float,
        routine: Dict[str, Any]
    ) -> List[str]:
        """Get specific recommendations for a feature based on its status"""
        recommendations = []
        feature_name = self.FEATURE_NAMES.get(feature_key, feature_key)
        
        # Feature-specific recommendations
        if feature_key == 'dark_circles':
            if status == 'stagnant':
                recommendations.append(f"👁️ {feature_name} stagnant - try caffeine eye cream or vitamin K serum")
            elif status == 'declining':
                recommendations.append(f"👁️ {feature_name} worsening - prioritize 8+ hours sleep and cold compress mornings")
        
        elif feature_key == 'puffiness':
            if status == 'stagnant':
                recommendations.append(f"💧 {feature_name} stagnant - sleep elevated, reduce sodium, try jade roller")
            elif status == 'declining':
                recommendations.append(f"💧 {feature_name} worsening - check for allergies, reduce salt, increase water intake")
        
        elif feature_key == 'brightness':
            if status == 'stagnant':
                recommendations.append(f"✨ {feature_name} stagnant - add vitamin C serum or gentle exfoliation 2x/week")
            elif status == 'declining':
                recommendations.append(f"✨ {feature_name} declining - increase hydration, add brightening serum, gentle exfoliation")
        
        elif feature_key == 'wrinkles':
            if status == 'stagnant':
                recommendations.append(f"📏 {feature_name} stagnant - consider adding retinol or peptide serum to routine")
            elif status == 'declining':
                recommendations.append(f"📏 {feature_name} worsening - add intensive moisturizer, retinol, and sun protection")
        
        elif feature_key == 'texture':
            if status == 'stagnant':
                recommendations.append(f"🧽 {feature_name} stagnant - try AHA/BHA exfoliation or hyaluronic acid serum")
            elif status == 'declining':
                recommendations.append(f"🧽 {feature_name} declining - gentle exfoliation, intensive hydration, check skincare routine")
        
        elif feature_key == 'pore_size':
            if status == 'stagnant':
                recommendations.append(f"🔍 {feature_name} stagnant - try niacinamide serum or salicylic acid cleanser")
            elif status == 'declining':
                recommendations.append(f"🔍 {feature_name} worsening - use clay mask 2x/week, salicylic acid, oil control products")
        
        return recommendations
    
    def _generate_first_time_summary(
        self, 
        current_analysis: Dict[str, Any],
        routine: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate summary for first-time users with no historical data"""
        sleep_score = current_analysis.get('sleep_score', 0)
        skin_score = current_analysis.get('skin_health_score', 0)
        features = current_analysis.get('features', {})
        
        # Find weakest areas
        sorted_features = sorted(features.items(), key=lambda x: x[1])
        weakest_features = sorted_features[:2]
        
        insights = [
            "📸 First analysis complete! We'll track your progress over time.",
            f"💤 Your Sleep Score is {sleep_score} and Skin Health Score is {skin_score}."
        ]
        
        # Add insights for weak areas
        for feature_key, value in weakest_features:
            feature_name = self.FEATURE_NAMES.get(feature_key, feature_key)
            feature_range = self.FEATURE_RANGES.get(feature_key, {})
            
            if value < feature_range.get('poor', 30):
                insights.append(f"⚠️ {feature_name} needs attention (score: {value:.0f})")
            elif value < feature_range.get('fair', 45):
                insights.append(f"🔍 {feature_name} has room for improvement (score: {value:.0f})")
        
        recommendations = [
            "📊 Take daily selfies to track trends and see what works for you",
            "💤 Aim for 7-8 hours of quality sleep each night",
            "💧 Stay hydrated with 8+ glasses of water daily"
        ]
        
        # Add specific recommendations for weak areas
        for feature_key, value in weakest_features:
            recs = self._get_feature_recommendations(feature_key, 'declining', value, routine)
            recommendations.extend(recs[:1])  # One rec per weak feature
        
        return {
            "daily_summary": f"Welcome! Your baseline Sleep Score is {sleep_score} and Skin Health Score is {skin_score}. Keep taking daily selfies to track your progress! 🌟",
            "key_insights": insights[:5],
            "recommendations": recommendations[:6],
            "trend_analysis": {
                "improving_features": [],
                "declining_features": [],
                "stagnant_features": [],
                "stable_features": list(features.keys())
            },
            "model": "Data-Driven Analysis (Baseline)",
            "provider": "internal",
            "data_points_analyzed": 1
        }


# Global instance
smart_summary_service = SmartSummaryService()
